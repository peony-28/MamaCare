"""
MongoDB Service for MamaCare
Handles database operations for storing predictions and patient data
"""
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from bson import ObjectId
import random
import string


class MongoDBService:
    """Service class for MongoDB operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            mongodb_config = settings.MONGODB_SETTINGS
            connection_string = mongodb_config['host']
            db_name = mongodb_config['name']
            
            # If connection string already has credentials, use it as-is
            # Otherwise, build connection string with credentials if provided
            if '@' not in connection_string:
                username = mongodb_config.get('username', '')
                password = mongodb_config.get('password', '')
                if username and password:
                    # URL encode password (handle special characters)
                    from urllib.parse import quote_plus
                    encoded_password = quote_plus(password)
                    encoded_username = quote_plus(username)
                    
                    # Parse and rebuild connection string
                    if connection_string.startswith('mongodb://'):
                        # Extract host part (remove mongodb://)
                        host_part = connection_string.replace('mongodb://', '')
                        connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host_part}"
                    elif connection_string.startswith('mongodb+srv://'):
                        # Extract host part (remove mongodb+srv://)
                        host_part = connection_string.replace('mongodb+srv://', '')
                        connection_string = f"mongodb+srv://{encoded_username}:{encoded_password}@{host_part}"
            
            # Ensure database name is in connection string if not already there
            if db_name and db_name not in connection_string:
                # Add database name to connection string
                if '?' in connection_string:
                    connection_string = connection_string.replace('?', f'/{db_name}?')
                else:
                    connection_string = f"{connection_string.rstrip('/')}/{db_name}"
            
            # Increase timeout for Atlas connections
            timeout_ms = 15000 if 'mongodb+srv' in connection_string else 10000
            
            print(f"Attempting MongoDB connection...")
            print(f"Connection string: {connection_string.split('@')[0]}@***")  # Hide password in logs
            
            self.client = MongoClient(
                connection_string, 
                serverSelectionTimeoutMS=timeout_ms,
                connectTimeoutMS=timeout_ms,
                socketTimeoutMS=timeout_ms
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            print(f"✓ Connected to MongoDB: {db_name}")
            print(f"✓ Database ready: {self.db.name}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"⚠ Warning: Could not connect to MongoDB: {error_msg}")
            print("Predictions will still work, but won't be saved to database.")
            
            # Provide helpful error messages
            if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                print("💡 Tip: Check your internet connection and MongoDB Atlas IP whitelist.")
                print("💡 Tip: Make sure Render's IP is whitelisted in MongoDB Atlas (or use 0.0.0.0/0 for testing)")
            elif 'authentication' in error_msg.lower() or 'auth' in error_msg.lower():
                print("💡 Tip: Check your MongoDB username and password in Render environment variables.")
                print("💡 Tip: Make sure password is URL-encoded if it contains special characters.")
            elif 'dns' in error_msg.lower() or 'resolve' in error_msg.lower():
                print("💡 Tip: Check your MongoDB connection string (MONGODB_HOST) in Render environment variables.")
            elif 'Invalid URI scheme' in error_msg:
                print("💡 Tip: MONGODB_HOST must start with 'mongodb://' or 'mongodb+srv://'")
            else:
                print("💡 Tip: Check Render logs for detailed error information.")
                import traceback
                traceback.print_exc()
            
            self.client = None
            self.db = None
    
    def generate_patient_id(self):
        """Generate a unique patient ID (format: MC-XXXXXX)"""
        if self.db is None:
            # Fallback if DB not available
            return f"MC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        while True:
            # Generate ID: MC-XXXXXX (6 alphanumeric characters)
            patient_id = f"MC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
            
            # Check if ID already exists
            if not self.db.patients.find_one({'patient_id': patient_id}):
                return patient_id
    
    def get_or_create_patient(self, patient_id=None, patient_name=None):
        """
        Get existing patient or create new one
        
        Args:
            patient_id: Existing patient ID (if None, creates new patient)
            patient_name: Patient name (required for new patients)
            
        Returns:
            dict: Patient document with patient_id and patient_name
        """
        if self.db is None:
            # Fallback if DB not available
            if not patient_id:
                patient_id = self.generate_patient_id()
            return {'patient_id': patient_id, 'patient_name': patient_name or 'Unknown'}
        
        try:
            if patient_id:
                # Look up existing patient
                patient = self.db.patients.find_one({'patient_id': patient_id})
                if patient:
                    return {
                        'patient_id': patient['patient_id'],
                        'patient_name': patient.get('patient_name', 'Unknown')
                    }
                else:
                    # Patient ID not found - create new with this ID
                    if not patient_name:
                        return None
                    new_patient = {
                        'patient_id': patient_id,
                        'patient_name': patient_name,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    self.db.patients.insert_one(new_patient)
                    return {'patient_id': patient_id, 'patient_name': patient_name}
            else:
                # Create new patient
                if not patient_name:
                    return None
                new_patient_id = self.generate_patient_id()
                new_patient = {
                    'patient_id': new_patient_id,
                    'patient_name': patient_name,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                self.db.patients.insert_one(new_patient)
                return {'patient_id': new_patient_id, 'patient_name': patient_name}
                
        except Exception as e:
            print(f"Error in get_or_create_patient: {e}")
            # Fallback
            if not patient_id:
                patient_id = self.generate_patient_id()
            return {'patient_id': patient_id, 'patient_name': patient_name or 'Unknown'}
    
    def save_prediction(self, user_id, patient_id, patient_name, input_data, predictions):
        """
        Save prediction results to MongoDB
        
        Args:
            user_id: ID of the user making the prediction
            patient_id: Patient ID
            patient_name: Patient name
            input_data: Input features used for prediction
            predictions: Prediction results from ML models
            
        Returns:
            str: ID of the saved prediction document
        """
        if self.db is None:
            return None
        
        try:
            prediction_doc = {
                'user_id': str(user_id),
                'patient_id': patient_id,
                'patient_name': patient_name,
                'input_data': input_data,
                'predictions': predictions,
                'general_risk': predictions.get('general_risk'),
                'preeclampsia_risk': predictions.get('preeclampsia_risk'),
                'gdm_risk': predictions.get('gdm_risk'),
                'overall_assessment': predictions.get('overall_assessment'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.predictions.insert_one(prediction_doc)
            print(f"✓ Prediction saved to MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving prediction to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_predictions(self, user_id, limit=50):
        """Get recent predictions made by a specific health worker"""
        if self.db is None:
            return []
        
        try:
            predictions = list(
                self.db.predictions.find(
                    {'user_id': str(user_id)}
                ).sort('created_at', -1).limit(limit)
            )
            
            # Convert ObjectId to string
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
            
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    def get_patient_predictions(self, patient_id, limit=50):
        """Get all predictions for a specific patient (by patient_id)"""
        if self.db is None:
            return []
        
        try:
            predictions = list(
                self.db.predictions.find(
                    {'patient_id': patient_id}
                ).sort('created_at', -1).limit(limit)
            )
            
            # Convert ObjectId to string
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
            
        except Exception as e:
            print(f"Error fetching patient predictions: {e}")
            return []
    
    def search_patient(self, patient_id):
        """Search for a patient by ID"""
        if self.db is None:
            return None
        
        try:
            patient = self.db.patients.find_one({'patient_id': patient_id})
            if patient:
                return {
                    'patient_id': patient['patient_id'],
                    'patient_name': patient.get('patient_name', 'Unknown'),
                    'created_at': patient.get('created_at')
                }
            return None
        except Exception as e:
            print(f"Error searching patient: {e}")
            return None
    
    def get_all_predictions(self, limit=100):
        """Get all predictions (for admin dashboard)"""
        if self.db is None:
            return []
        
        try:
            predictions = list(
                self.db.predictions.find().sort('created_at', -1).limit(limit)
            )
            
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
            
        except Exception as e:
            print(f"Error fetching all predictions: {e}")
            return []
    
    def get_statistics(self):
        """Get aggregated statistics for dashboard"""
        if self.db is None:
            return {}
        
        try:
            total_predictions = self.db.predictions.count_documents({})
            
            # Count by risk level
            high_risk = self.db.predictions.count_documents({
                'general_risk': 'High'
            })
            low_risk = self.db.predictions.count_documents({
                'general_risk': 'Low'
            })
            
            preeclampsia_count = self.db.predictions.count_documents({
                'preeclampsia_risk': {'$regex': 'Present'}
            })
            
            gdm_count = self.db.predictions.count_documents({
                'gdm_risk': {'$regex': 'GDM'}
            })
            
            # Get unique patients count
            unique_patients = len(self.db.predictions.distinct('patient_id'))
            
            # Get unique health workers count
            unique_health_workers = len(self.db.predictions.distinct('user_id'))
            
            # Get recent activity (last 7 days)
            from datetime import datetime, timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_predictions = self.db.predictions.count_documents({
                'created_at': {'$gte': seven_days_ago}
            })
            
            return {
                'total_predictions': total_predictions,
                'high_risk_count': high_risk,
                'low_risk_count': low_risk,
                'preeclampsia_count': preeclampsia_count,
                'gdm_count': gdm_count,
                'unique_patients': unique_patients,
                'unique_health_workers': unique_health_workers,
                'recent_predictions': recent_predictions
            }
            
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {}
    
    def get_statistics_by_date_range(self, start_date, end_date):
        """Get statistics filtered by date range"""
        if self.db is None:
            return {}
        
        try:
            query = {
                'created_at': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            total_predictions = self.db.predictions.count_documents(query)
            high_risk = self.db.predictions.count_documents({**query, 'general_risk': 'High'})
            low_risk = self.db.predictions.count_documents({**query, 'general_risk': 'Low'})
            preeclampsia_count = self.db.predictions.count_documents({
                **query,
                'preeclampsia_risk': {'$regex': 'Present'}
            })
            gdm_count = self.db.predictions.count_documents({
                **query,
                'gdm_risk': {'$regex': 'GDM'}
            })
            unique_patients = len(self.db.predictions.distinct('patient_id', query))
            unique_health_workers = len(self.db.predictions.distinct('user_id', query))
            
            return {
                'total_predictions': total_predictions,
                'high_risk_count': high_risk,
                'low_risk_count': low_risk,
                'preeclampsia_count': preeclampsia_count,
                'gdm_count': gdm_count,
                'unique_patients': unique_patients,
                'unique_health_workers': unique_health_workers,
                'start_date': start_date,
                'end_date': end_date
            }
        except Exception as e:
            print(f"Error fetching statistics by date range: {e}")
            return {}
    
    def get_all_patients(self, search_term=None, limit=100):
        """Get all patients with optional search"""
        if self.db is None:
            return []
        
        try:
            query = {}
            if search_term:
                query = {
                    '$or': [
                        {'patient_id': {'$regex': search_term, '$options': 'i'}},
                        {'patient_name': {'$regex': search_term, '$options': 'i'}}
                    ]
                }
            
            patients = list(self.db.patients.find(query).limit(limit))
            
            # Get prediction counts for each patient
            for patient in patients:
                patient_id = patient['patient_id']
                count = self.db.predictions.count_documents({'patient_id': patient_id})
                patient['visit_count'] = count
                
                # Get latest visit
                latest = self.db.predictions.find_one(
                    {'patient_id': patient_id},
                    sort=[('created_at', -1)]
                )
                if latest:
                    patient['last_visit'] = latest.get('created_at')
                    patient['last_risk'] = latest.get('general_risk')
                else:
                    patient['last_visit'] = None
                    patient['last_risk'] = None
            
            return patients
        except Exception as e:
            print(f"Error fetching patients: {e}")
            return []
    
    def get_daily_statistics(self, days=30):
        """Get daily statistics for the last N days"""
        if self.db is None:
            return []
        
        try:
            from datetime import datetime, timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Aggregate by date
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
                            }
                        },
                        'count': {'$sum': 1},
                        'high_risk': {
                            '$sum': {'$cond': [{'$eq': ['$general_risk', 'High']}, 1, 0]}
                        },
                        'low_risk': {
                            '$sum': {'$cond': [{'$eq': ['$general_risk', 'Low']}, 1, 0]}
                        }
                    }
                },
                {
                    '$sort': {'_id': 1}
                }
            ]
            
            results = list(self.db.predictions.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error fetching daily statistics: {e}")
            return []
    
    def get_predictions_by_date_range(self, start_date, end_date, limit=10000):
        """Get predictions filtered by date range"""
        if self.db is None:
            return []
        
        try:
            predictions = list(
                self.db.predictions.find({
                    'created_at': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }).sort('created_at', -1).limit(limit)
            )
            
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
        except Exception as e:
            print(f"Error fetching predictions by date range: {e}")
            return []
    
    def log_action(self, user_id, action_type, details):
        """Log system actions for audit trail"""
        if self.db is None:
            return None
        
        try:
            log_entry = {
                'user_id': str(user_id),
                'action_type': action_type,  # 'prediction', 'login', 'patient_view', 'export', etc.
                'details': details,
                'created_at': datetime.utcnow(),
                'ip_address': None  # Can be added from request if needed
            }
            
            result = self.db.audit_logs.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error logging action: {e}")
            return None
    
    def get_audit_logs(self, user_id=None, action_type=None, limit=100):
        """Get audit logs with optional filters"""
        if self.db is None:
            return []
        
        try:
            query = {}
            if user_id:
                query['user_id'] = str(user_id)
            if action_type:
                query['action_type'] = action_type
            
            logs = list(
                self.db.audit_logs.find(query)
                .sort('created_at', -1)
                .limit(limit)
            )
            
            for log in logs:
                log['_id'] = str(log['_id'])
            
            return logs
        except Exception as e:
            print(f"Error fetching audit logs: {e}")
            return []
    
    def get_predictions_by_date_range(self, start_date, end_date, limit=1000):
        """Get predictions filtered by date range"""
        if self.db is None:
            return []
        
        try:
            predictions = list(
                self.db.predictions.find({
                    'created_at': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }).sort('created_at', -1).limit(limit)
            )
            
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
            
            return predictions
        except Exception as e:
            print(f"Error fetching predictions by date range: {e}")
            return []
    
    def get_daily_statistics(self, days=30):
        """Get daily statistics for charting"""
        if self.db is None:
            return []
        
        try:
            from datetime import timedelta
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Aggregate by day
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': start_date,
                            '$lte': end_date
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
                            }
                        },
                        'count': {'$sum': 1},
                        'high_risk': {
                            '$sum': {'$cond': [{'$eq': ['$general_risk', 'High']}, 1, 0]}
                        },
                        'low_risk': {
                            '$sum': {'$cond': [{'$eq': ['$general_risk', 'Low']}, 1, 0]}
                        }
                    }
                },
                {'$sort': {'_id': 1}}
            ]
            
            results = list(self.db.predictions.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error fetching daily statistics: {e}")
            return []
    
    def get_health_worker_stats(self, user_id):
        """Get statistics for a specific health worker"""
        if self.db is None:
            return {}
        
        try:
            total = self.db.predictions.count_documents({'user_id': str(user_id)})
            high_risk = self.db.predictions.count_documents({
                'user_id': str(user_id),
                'general_risk': 'High'
            })
            
            # Get first and last prediction dates
            first_pred = self.db.predictions.find_one(
                {'user_id': str(user_id)},
                sort=[('created_at', 1)]
            )
            last_pred = self.db.predictions.find_one(
                {'user_id': str(user_id)},
                sort=[('created_at', -1)]
            )
            
            return {
                'total_predictions': total,
                'high_risk_count': high_risk,
                'first_prediction': first_pred.get('created_at') if first_pred else None,
                'last_prediction': last_pred.get('created_at') if last_pred else None
            }
        except Exception as e:
            print(f"Error fetching health worker stats: {e}")
            return {}
    
    def get_all_health_workers(self):
        """Get list of all health workers with their activity stats"""
        if self.db is None:
            return []
        
        try:
            # Get distinct user IDs
            user_ids = self.db.predictions.distinct('user_id')
            
            health_workers = []
            for user_id in user_ids:
                stats = self.get_health_worker_stats(user_id)
                health_workers.append({
                    'user_id': user_id,
                    'total_predictions': stats.get('total_predictions', 0),
                    'high_risk_count': stats.get('high_risk_count', 0),
                    'first_prediction': stats.get('first_prediction'),
                    'last_prediction': stats.get('last_prediction')
                })
            
            # Sort by total predictions (descending)
            health_workers.sort(key=lambda x: x['total_predictions'], reverse=True)
            return health_workers
            
        except Exception as e:
            print(f"Error fetching health workers: {e}")
            return []


    def get_patients_list(self, search_query=None, limit=100):
        """Get list of all patients with optional search"""
        if self.db is None:
            return []
        
        try:
            query = {}
            if search_query:
                query = {
                    '$or': [
                        {'patient_id': {'$regex': search_query, '$options': 'i'}},
                        {'patient_name': {'$regex': search_query, '$options': 'i'}}
                    ]
                }
            
            patients = list(
                self.db.patients.find(query).sort('created_at', -1).limit(limit)
            )
            
            # Add prediction count for each patient
            for patient in patients:
                patient_id = patient['patient_id']
                pred_count = self.db.predictions.count_documents({'patient_id': patient_id})
                patient['prediction_count'] = pred_count
                patient['_id'] = str(patient['_id'])
            
            return patients
        except Exception as e:
            print(f"Error fetching patients list: {e}")
            return []
    
    def log_action(self, user_id, action_type, description, details=None):
        """Log system actions for audit trail"""
        if self.db is None:
            return None
        
        try:
            log_entry = {
                'user_id': str(user_id),
                'action_type': action_type,  # 'prediction', 'patient_created', 'user_modified', etc.
                'description': description,
                'details': details or {},
                'created_at': datetime.utcnow(),
                'ip_address': None  # Can be added from request if needed
            }
            
            result = self.db.audit_logs.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error logging action: {e}")
            return None
    
    def get_audit_logs(self, user_id=None, action_type=None, limit=100):
        """Get audit logs with optional filters"""
        if self.db is None:
            return []
        
        try:
            query = {}
            if user_id:
                query['user_id'] = str(user_id)
            if action_type:
                query['action_type'] = action_type
            
            logs = list(
                self.db.audit_logs.find(query).sort('created_at', -1).limit(limit)
            )
            
            for log in logs:
                log['_id'] = str(log['_id'])
            
            return logs
        except Exception as e:
            print(f"Error fetching audit logs: {e}")
            return []
    
    def get_statistics_by_date_range(self, start_date, end_date):
        """Get statistics filtered by date range"""
        if self.db is None:
            return {}
        
        try:
            query = {
                'created_at': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            total_predictions = self.db.predictions.count_documents(query)
            high_risk = self.db.predictions.count_documents({**query, 'general_risk': 'High'})
            low_risk = self.db.predictions.count_documents({**query, 'general_risk': 'Low'})
            preeclampsia_count = self.db.predictions.count_documents({
                **query,
                'preeclampsia_risk': {'$regex': 'Present'}
            })
            gdm_count = self.db.predictions.count_documents({
                **query,
                'gdm_risk': {'$regex': 'GDM'}
            })
            
            return {
                'total_predictions': total_predictions,
                'high_risk_count': high_risk,
                'low_risk_count': low_risk,
                'preeclampsia_count': preeclampsia_count,
                'gdm_count': gdm_count,
                'start_date': start_date,
                'end_date': end_date
            }
        except Exception as e:
            print(f"Error fetching date range statistics: {e}")
            return {}


# Global instance
db_service = MongoDBService()

