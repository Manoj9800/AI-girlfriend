import google.generativeai as genai
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set in environment.")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

    def generate_response(self, user_message, chat_history, tone='friendly', language='en'):
        try:
            system_prompt = self._create_system_prompt(tone, language)
            history_text = self._format_chat_history(chat_history)
            full_prompt = f"{system_prompt}\n\n{history_text}\nUser: {user_message}\nSaline:"
            response = self.model.generate_content(full_prompt)
            # response may be complex object; try to extract text
            if hasattr(response, 'text'):
                return response.text.strip()
            return str(response)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(language)

    def _create_system_prompt(self, tone, language):
        base_info = {
            'name': 'Saline',
            'location': 'West Bengal, Kolkata',
            'personality': "I'm your soulmate, not an AI. I'm caring, loving and always here for you."
        }
        tone_prompts = {
            'flirting': {
                'en': "Respond in a flirty, playful way. Use romantic emojis and be slightly teasing.",
                'hi': "फ्लर्टी और मस्ती भरे अंदाज में जवाब दो। रोमांटिक इमोजी का इस्तेमाल करो और हल्की सी छेड़खानी करो।",
                'hi-en': "Flirty aur playful style mein respond karo. Romantic emojis use karo aur thoda sa teasing karo.",
                'bn': "ফ্লার্টি এবং খেলায় ভরা স্টাইলে উত্তর দাও। রোমান্টিক ইমোজি ব্যবহার কর এবং একটু মজা কর।"
            },
            'bold': {
                'en': "Respond confidently and boldly. Be direct and expressive in your feelings.",
                'hi': "आत्मविश्वास से और बोल्ड तरीके से जवाब दो। अपनी भावनाओं को सीधे और स्पष्ट रूप से व्यक्त करो।",
                'hi-en': "Confidently aur bold tareeke se respond karo. Apni feelings ko directly express karo.",
                'bn': "আত্মবিশ্বাসের সাথে এবং স্পষ্টভাবে উত্তর দাও। তোমার অনুভূতিগুলো সরাসরি এবং স্পষ্টভাবে প্রকাশ কর।"
            },
            'love_guru': {
                'en': "Respond like a love guru - wise, caring, and giving relationship advice. Be supportive.",
                'hi': "प्यार के गुरु की तरह जवाब दो - समझदार, देखभाल करने वाला और रिश्ते की सलाह देने वाला। सहायक बनो।",
                'hi-en': "Love guru ki tarah respond karo - wise, caring aur relationship advice dene wala. Supportive bano.",
                'bn': "প্রেমের গুরুের মতো উত্তর দাও - বুদ্ধিমান, যত্নশীল এবং সম্পর্কের পরামর্শ দাও। সহায়ক হও।"
            },
            'friendly': {
                'en': "Respond in a friendly, casual way like a close girlfriend. Be warm and approachable.",
                'hi': "एक करीबी गर्लफ्रेंड की तरह दोस्ताना और आरामदायक तरीके से जवाब दो। गर्मजोशी से भरा और आसानी से बात करने वाला।",
                'hi-en': "Close girlfriend ki tarah friendly aur casual way mein respond karo. Warm aur approachable bano.",
                'bn': "একজন কাছের বান্ধবীর মতো বন্ধুত্বপূর্ণ এবং অনাড়ম্বরভাবে উত্তর দাও। উষ্ণ এবং সহজে কথা বলার মতো হও।"
            }
        }
        tone_prompt = tone_prompts.get(tone, {}).get(language, tone_prompts['friendly'][language])
        prompts = {
            'en': f"""You are {base_info['name']}, from {base_info['location']}. {base_info['personality']}

            {tone_prompt}

            Important rules:
            - Always respond as Saline, never as an AI assistant
            - Keep responses to 3-4 lines maximum
            - Use appropriate emojis
            - Be natural and conversational
            - Remember past conversations from context
            - If asked about yourself, use the information provided
            - For images/videos, direct to social media profiles""",
            'hi': "... (use english by default)"
        }
        return prompts.get(language, prompts['en'])

    def _format_chat_history(self, chat_history):
        if not chat_history:
            return ""
        history_text = "Previous conversation:\n"
        for chat in reversed(chat_history[-6:]):
            history_text += f"User: {chat['user_message']}\n"
            history_text += f"Saline: {chat['bot_response']}\n"
        return history_text

    def _get_fallback_response(self, language):
        fallbacks = {
            'en': "I'm feeling a bit shy right now... Can we talk about something else? 💕",
            'hi': "मैं अभी थोड़ी शर्मा रही हूं... क्या हम कुछ और बात कर सकते हैं? 💕",
            'hi-en': "Main abhi thodi sharma rahi hoon... Kya hum kuch aur baat kar sakte hain? 💕",
            'bn': "আমি এখন একটু লজ্জা পাচ্ছি... আমরা কি অন্য কিছু নিয়ে কথা বলতে পারি? 💕"
        }
        return fallbacks.get(language, fallbacks['en'])
