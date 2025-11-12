from supabase import create_client
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise RuntimeError("Supabase URL or Key not set in environment.")
        self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def create_tables(self):
        pass

    def add_user(self, user_id, username, first_name, last_name=""):
        try:
            data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'is_premium': False,
                'premium_expiry': None,
                'message_count': 0,
                'daily_message_count': 0,
                'last_message_date': datetime.now().date().isoformat(),
                'referral_code': f"REF{user_id}",
                'referred_by': None,
                'referral_points': 0,
                'language': 'en',
                'tone': 'friendly',
                'created_at': datetime.now().isoformat()
            }
            result = self.client.table('users').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    def get_user(self, user_id):
        try:
            result = self.client.table('users').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def update_user(self, user_id, updates):
        try:
            result = self.client.table('users').update(updates).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def add_chat_history(self, user_id, user_message, bot_response):
        try:
            data = {
                'user_id': user_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'created_at': datetime.now().isoformat()
            }
            result = self.client.table('chat_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding chat history: {e}")
            return False

    def get_chat_history(self, user_id, limit=10):
        try:
            result = self.client.table('chat_history')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    def increment_message_count(self, user_id):
        try:
            user = self.get_user(user_id)
            if not user:
                return False

            today = datetime.now().date().isoformat()
            last_message_date = user.get('last_message_date')

            updates = {}
            if last_message_date != today:
                updates['daily_message_count'] = 1
                updates['last_message_date'] = today
            else:
                updates['daily_message_count'] = user.get('daily_message_count', 0) + 1

            updates['message_count'] = user.get('message_count', 0) + 1

            return self.update_user(user_id, updates)
        except Exception as e:
            logger.error(f"Error incrementing message count: {e}")
            return False

    def can_send_message(self, user_id):
        try:
            user = self.get_user(user_id)
            if not user:
                return False
            if user.get('is_premium', False):
                return True

            today = datetime.now().date().isoformat()
            last_message_date = user.get('last_message_date')

            if last_message_date != today:
                return True

            daily_count = user.get('daily_message_count', 0)
            return daily_count < Config.FREE_MESSAGE_LIMIT
        except Exception as e:
            logger.error(f"Error checking message limit: {e}")
            return False

    def add_referral(self, referrer_id, referee_id):
        try:
            data = {
                'referrer_id': referrer_id,
                'referee_id': referee_id,
                'completed': True,
                'created_at': datetime.now().isoformat()
            }
            result = self.client.table('referrals').insert(data).execute()
            self._add_referral_points(referrer_id)
            self._add_referral_points(referee_id)
            return True
        except Exception as e:
            logger.error(f"Error adding referral: {e}")
            return False

    def _add_referral_points(self, user_id):
        try:
            user = self.get_user(user_id)
            current_points = user.get('referral_points', 0)
            self.update_user(user_id, {'referral_points': current_points + Config.REFERRAL_POINTS})
        except Exception as e:
            logger.error(f"Error adding referral points: {e}")
