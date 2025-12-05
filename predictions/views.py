"""
Views for MamaCare prediction system
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from .forms import PredictionForm, UserRegistrationForm
from .ml_service import ml_service
from .db_service import db_service


def register_view(request):
    """User registration view for health workers"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Health workers are regular users (not staff/admin by default)
            user.is_staff = False
            user.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'predictions/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Log login
            db_service.log_action(user.id, 'login', {'username': username})
            return redirect('predict')
        else:
            messages.error(request, 'Invalid username or password.')
            # Log failed login attempt
            db_service.log_action(None, 'login_failed', {'username': username})
    
    return render(request, 'predictions/login.html')


@login_required
def predict_view(request):
    """Main prediction view"""
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            # Get cleaned form data
            input_data = form.cleaned_data
            
            # Handle patient ID and name
            patient_id_input = input_data.pop('patient_id', '').strip()
            patient_name = input_data.pop('patient_name', '').strip()
            
            if not patient_name:
                messages.error(request, 'Patient name is required.')
                return render(request, 'predictions/predict.html', {'form': form})
            
            # Get or create patient
            patient = db_service.get_or_create_patient(
                patient_id=patient_id_input if patient_id_input else None,
                patient_name=patient_name
            )
            
            if not patient:
                messages.error(request, 'Error creating/retrieving patient record.')
                return render(request, 'predictions/predict.html', {'form': form})
            
            patient_id = patient['patient_id']
            patient_name = patient['patient_name']
            
            # Make prediction using ML service
            try:
                predictions = ml_service.predict_all_risks(input_data)
                
                # Log prediction action
                db_service.log_action(request.user.id, 'prediction_made', {
                    'patient_id': patient_id,
                    'general_risk': predictions.get('general_risk'),
                    'preeclampsia_risk': predictions.get('preeclampsia_risk'),
                    'gdm_risk': predictions.get('gdm_risk')
                })
                
                # Save to database (optional - predictions work without it)
                prediction_id = db_service.save_prediction(
                    user_id=request.user.id,
                    patient_id=patient_id,
                    patient_name=patient_name,
                    input_data=input_data,
                    predictions=predictions
                )
                
                if prediction_id:
                    messages.success(request, f'Prediction saved successfully! Patient ID: {patient_id}')
                else:
                    # Only show warning if DEBUG is True (to avoid confusing users in production)
                    if settings.DEBUG:
                        messages.info(request, f'Prediction completed! Patient ID: {patient_id} (Database save disabled - configure MongoDB in .env to enable saving)')
                    else:
                        messages.success(request, f'Prediction completed successfully! Patient ID: {patient_id}')
                
                # Render results
                return render(request, 'predictions/result.html', {
                    'form': form,
                    'predictions': predictions,
                    'input_data': input_data,
                    'patient_id': patient_id,
                    'patient_name': patient_name
                })
                
            except Exception as e:
                messages.error(request, f'Error making prediction: {str(e)}')
    else:
        form = PredictionForm()
    
    return render(request, 'predictions/predict.html', {'form': form})


@login_required
def dashboard_view(request):
    """Dashboard view - shows user's own predictions for health workers, system-wide for admins"""
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if request.user.is_staff:
        # Admin view: system-wide statistics and all predictions
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                stats = db_service.get_statistics_by_date_range(start, end)
                all_predictions = db_service.get_predictions_by_date_range(start, end, limit=20)
            except ValueError:
                stats = db_service.get_statistics()
                all_predictions = db_service.get_all_predictions(limit=20)
        else:
            stats = db_service.get_statistics()
            all_predictions = db_service.get_all_predictions(limit=20)
        
        health_workers_data = db_service.get_all_health_workers()
        
        # Get user details for top health workers
        top_health_workers = []
        for hw in health_workers_data[:10]:  # Top 10 most active
            try:
                user = User.objects.get(id=int(hw['user_id']))
                top_health_workers.append({
                    'user': user,
                    'user_id': hw['user_id'],
                    'total_predictions': hw['total_predictions'],
                    'high_risk_count': hw['high_risk_count'],
                    'last_prediction': hw.get('last_prediction')
                })
            except (User.DoesNotExist, ValueError, TypeError):
                top_health_workers.append({
                    'user': None,
                    'user_id': hw['user_id'],
                    'total_predictions': hw['total_predictions'],
                    'high_risk_count': hw['high_risk_count'],
                    'last_prediction': hw.get('last_prediction')
                })
        
        # Get daily statistics for charts
        daily_stats = db_service.get_daily_statistics(days=30)
        
        # Log dashboard view
        db_service.log_action(request.user.id, 'dashboard_view', {'is_staff': True})
        
        return render(request, 'predictions/dashboard.html', {
            'all_predictions': all_predictions,
            'stats': stats,
            'is_staff': True,
            'user_predictions': None,
            'health_workers': top_health_workers,
            'daily_stats': daily_stats,
            'start_date': start_date,
            'end_date': end_date
        })
    else:
        # Health worker view: their own predictions
        user_predictions = db_service.get_user_predictions(request.user.id, limit=20)
        
        # Log dashboard view
        db_service.log_action(request.user.id, 'dashboard_view', {'is_staff': False})
        
        return render(request, 'predictions/dashboard.html', {
            'user_predictions': user_predictions,
            'stats': {},
            'is_staff': False,
            'all_predictions': None,
            'health_workers': None,
            'daily_stats': None
        })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def health_workers_view(request):
    """Admin view: List all health workers with their activity"""
    health_workers_data = db_service.get_all_health_workers()
    
    # Get user details for each health worker
    health_worker_details = []
    for hw in health_workers_data:
        try:
            user = User.objects.get(id=int(hw['user_id']))
            health_worker_details.append({
                'user': user,
                'user_id': hw['user_id'],
                'total_predictions': hw['total_predictions'],
                'high_risk_count': hw['high_risk_count'],
                'first_prediction': hw.get('first_prediction'),
                'last_prediction': hw.get('last_prediction')
            })
        except (User.DoesNotExist, ValueError, TypeError):
            # User might have been deleted
            health_worker_details.append({
                'user': None,
                'user_id': hw['user_id'],
                'total_predictions': hw['total_predictions'],
                'high_risk_count': hw['high_risk_count'],
                'first_prediction': hw.get('first_prediction'),
                'last_prediction': hw.get('last_prediction')
            })
    
    return render(request, 'predictions/health_workers.html', {
        'health_workers': health_worker_details
    })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def health_worker_detail_view(request, user_id):
    """Admin view: Detailed view of a specific health worker's activity"""
    try:
        user = User.objects.get(id=user_id)
        stats = db_service.get_health_worker_stats(user_id)
        predictions = db_service.get_user_predictions(user_id, limit=50)
        
        # Log action
        db_service.log_action(request.user.id, 'health_worker_view', {'viewed_user_id': user_id})
        
        return render(request, 'predictions/health_worker_detail.html', {
            'health_worker': user,
            'stats': stats,
            'predictions': predictions
        })
    except User.DoesNotExist:
        messages.error(request, 'Health worker not found.')
        return redirect('health_workers')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def patients_management_view(request):
    """Admin view: Patient management with search and filter"""
    search_term = request.GET.get('search', '').strip()
    patients = db_service.get_all_patients(search_term=search_term if search_term else None, limit=100)
    
    # Log action
    db_service.log_action(request.user.id, 'patients_management_view', {'search_term': search_term})
    
    return render(request, 'predictions/patients_management.html', {
        'patients': patients,
        'search_term': search_term
    })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def users_management_view(request):
    """Admin view: User management - activate/deactivate accounts"""
    users = User.objects.all().order_by('-date_joined')
    
    # Handle activation/deactivation
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            user = User.objects.get(id=user_id)
            if action == 'activate':
                user.is_active = True
                user.save()
                messages.success(request, f'User {user.username} has been activated.')
                db_service.log_action(request.user.id, 'user_activated', {'target_user_id': user_id})
            elif action == 'deactivate':
                user.is_active = False
                user.save()
                messages.success(request, f'User {user.username} has been deactivated.')
                db_service.log_action(request.user.id, 'user_deactivated', {'target_user_id': user_id})
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    # Log view
    db_service.log_action(request.user.id, 'users_management_view', {})
    
    return render(request, 'predictions/users_management.html', {
        'users': users
    })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def audit_logs_view(request):
    """Admin view: System audit logs"""
    user_id = request.GET.get('user_id')
    action_type = request.GET.get('action_type')
    limit = int(request.GET.get('limit', 100))
    
    logs = db_service.get_audit_logs(
        user_id=user_id if user_id else None,
        action_type=action_type if action_type else None,
        limit=limit
    )
    
    # Get user names for logs
    for log in logs:
        try:
            user = User.objects.get(id=int(log['user_id']))
            log['user_name'] = user.get_full_name() or user.username
        except (User.DoesNotExist, ValueError, TypeError):
            log['user_name'] = f"User ID: {log['user_id']}"
    
    return render(request, 'predictions/audit_logs.html', {
        'logs': logs,
        'selected_user_id': user_id or '',
        'selected_action_type': action_type or ''
    })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def export_csv_view(request):
    """Export predictions to CSV"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            predictions = db_service.get_predictions_by_date_range(start, end, limit=10000)
        except ValueError:
            predictions = db_service.get_all_predictions(limit=10000)
    else:
        predictions = db_service.get_all_predictions(limit=10000)
    
    # Log export
    db_service.log_action(request.user.id, 'export_csv', {
        'start_date': start_date,
        'end_date': end_date,
        'count': len(predictions)
    })
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mamacare_predictions_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Patient ID', 'Patient Name', 'Health Worker ID', 'Age', 'BMI', 
        'Gestational Age', 'Systolic BP', 'Diastolic BP', 'General Risk', 
        'Preeclampsia Risk', 'GDM Risk', 'Overall Assessment'
    ])
    
    for pred in predictions:
        input_data = pred.get('input_data', {})
        writer.writerow([
            pred.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if pred.get('created_at') else '',
            pred.get('patient_id', ''),
            pred.get('patient_name', ''),
            pred.get('user_id', ''),
            input_data.get('age', ''),
            input_data.get('bmi_val', ''),
            input_data.get('gestational_age_weeks', ''),
            input_data.get('systolic_bp', ''),
            input_data.get('diastolic_bp', ''),
            pred.get('general_risk', ''),
            pred.get('preeclampsia_risk', ''),
            pred.get('gdm_risk', ''),
            pred.get('overall_assessment', '')
        ])
    
    return response


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def analytics_charts_view(request):
    """Admin view: Analytics with visual charts"""
    days = int(request.GET.get('days', 30))
    daily_stats = db_service.get_daily_statistics(days=days)
    stats = db_service.get_statistics()
    
    # Prepare data for charts
    chart_data = {
        'dates': [item['_id'] for item in daily_stats],
        'counts': [item['count'] for item in daily_stats],
        'high_risk': [item['high_risk'] for item in daily_stats],
        'low_risk': [item['low_risk'] for item in daily_stats]
    }
    
    return render(request, 'predictions/analytics.html', {
        'stats': stats,
        'chart_data': chart_data,
        'days': days
    })


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/predict/')
def analytics_data_api(request):
    """API endpoint for chart data"""
    days = int(request.GET.get('days', 30))
    daily_stats = db_service.get_daily_statistics(days=days)
    
    # Get all predictions for condition trends
    all_predictions = db_service.get_all_predictions(limit=10000)
    
    # Group by date for conditions
    condition_by_date = {}
    for pred in all_predictions:
        pred_date = pred.get('created_at')
        if pred_date:
            if isinstance(pred_date, datetime):
                date_key = pred_date.strftime('%Y-%m-%d')
            else:
                date_key = str(pred_date)[:10]
            
            if date_key not in condition_by_date:
                condition_by_date[date_key] = {'preeclampsia': 0, 'gdm': 0}
            
            if 'Present' in str(pred.get('preeclampsia_risk', '')):
                condition_by_date[date_key]['preeclampsia'] += 1
            if 'GDM' in str(pred.get('gdm_risk', '')):
                condition_by_date[date_key]['gdm'] += 1
    
    dates = [item['_id'] for item in daily_stats]
    preeclampsia_data = [condition_by_date.get(d, {}).get('preeclampsia', 0) for d in dates]
    gdm_data = [condition_by_date.get(d, {}).get('gdm', 0) for d in dates]
    
    return JsonResponse({
        'dates': dates,
        'total': [item['count'] for item in daily_stats],
        'high_risk': [item['high_risk'] for item in daily_stats],
        'low_risk': [item['low_risk'] for item in daily_stats],
        'preeclampsia': preeclampsia_data,
        'gdm': gdm_data
    })


@login_required
def history_view(request):
    """View prediction history - supports patient ID lookup"""
    patient_id = request.GET.get('patient_id', '').strip()
    
    if patient_id:
        # Look up patient by ID (any health worker can access any patient)
        patient = db_service.search_patient(patient_id)
        if patient:
            predictions = db_service.get_patient_predictions(patient_id, limit=50)
            return render(request, 'predictions/history.html', {
                'predictions': predictions,
                'patient_id': patient_id,
                'patient_name': patient['patient_name'],
                'is_patient_view': True
            })
        else:
            messages.warning(request, f'Patient ID "{patient_id}" not found.')
    
    # Default: show user's own predictions
    predictions = db_service.get_user_predictions(request.user.id, limit=50)
    
    return render(request, 'predictions/history.html', {
        'predictions': predictions,
        'patient_id': None,
        'is_patient_view': False
    })


@login_required
def patient_detail_view(request, patient_id):
    """Detailed patient view showing all visits with comparison"""
    # Log patient view
    db_service.log_action(request.user.id, 'patient_view', {'patient_id': patient_id})
    
    # Get patient information
    patient = db_service.search_patient(patient_id)
    if not patient:
        messages.error(request, f'Patient ID "{patient_id}" not found.')
        return redirect('history')
    
    # Get all predictions for this patient, sorted by date (newest first)
    predictions = db_service.get_patient_predictions(patient_id, limit=100)
    
    if not predictions:
        messages.warning(request, f'No predictions found for patient {patient_id}.')
        return redirect('history')
    
    # Sort by date (newest first) for display
    predictions.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    
    # Prepare data for comparison view
    # Group predictions with their key metrics for easy comparison
    comparison_data = []
    for pred in predictions:
        input_data = pred.get('input_data', {})
        user_id = pred.get('user_id')
        
        # Get health worker information
        health_worker_name = 'Unknown'
        if user_id:
            try:
                user = User.objects.get(id=int(user_id))
                health_worker_name = f"{user.get_full_name() or user.username}"
            except (User.DoesNotExist, ValueError, TypeError):
                health_worker_name = f"User ID: {user_id}"
        
        comparison_data.append({
            'date': pred.get('created_at'),
            'prediction_id': str(pred.get('_id', '')),
            'health_worker': health_worker_name,
            'user_id': user_id,
            'vitals': {
                'age': input_data.get('age'),
                'systolic_bp': input_data.get('systolic_bp'),
                'diastolic_bp': input_data.get('diastolic_bp'),
                'heart_rate': input_data.get('heart_rate'),
                'body_temp': input_data.get('body_temp'),
                'bmi': input_data.get('bmi_val'),
            },
            'pregnancy': {
                'gestational_age': input_data.get('gestational_age_weeks'),
                'gravida': input_data.get('gravida'),
                'parity': input_data.get('parity'),
            },
            'lab_values': {
                'hemoglobin': input_data.get('hemoglobin_val'),
                'blood_sugar': input_data.get('bs'),
                'hdl': input_data.get('hdl'),
                'ogtt': input_data.get('ogtt'),
            },
            'fetal': {
                'fetal_weight': input_data.get('fetal_weight_kgs'),
                'amniotic_fluid': input_data.get('amniotic_fluid_levels_cm'),
                'protein_uria': input_data.get('protein_uria'),
            },
            'risks': {
                'general_risk': pred.get('general_risk'),
                'preeclampsia_risk': pred.get('preeclampsia_risk'),
                'gdm_risk': pred.get('gdm_risk'),
                'overall_assessment': pred.get('overall_assessment'),
            }
        })
    
    return render(request, 'predictions/patient_detail.html', {
        'patient': patient,
        'patient_id': patient_id,
        'predictions': predictions,
        'comparison_data': comparison_data,
        'total_visits': len(predictions)
    })


def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('predict')
    return render(request, 'predictions/home.html')

