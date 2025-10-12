import requests
import json
from typing import Dict, Any

class ChatAgent:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"  # Default Groq model
    
    def get_response(self, prompt, context=None):
        """
        Get response from Groq API for travel-related queries
        """
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the messages
        messages = []
        
        # Add system context for travel planning
        system_message = {
            "role": "system",
            "content": """You are a helpful travel assistant specializing in finding hotels, restaurants, and travel recommendations. 
            Provide detailed, accurate, and well-formatted responses. Include specific names, ratings, prices when possible, 
            and organize information in a clear, readable format. Focus on practical and actionable advice."""
        }
        messages.append(system_message)
        
        # Add context if provided
        if context:
            context_message = {
                "role": "user", 
                "content": f"Context: {context}"
            }
            messages.append(context_message)
        
        # Add the main prompt
        user_message = {
            "role": "user",
            "content": prompt
        }
        messages.append(user_message)
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"Error connecting to AI service: {str(e)}"
        except KeyError as e:
            return f"Error parsing AI response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def find_hotels(self, destination, num_days, budget, hotel_rating, travel_theme=None):
        """
        Find hotels using AI recommendations
        """
        prompt = f"""
        Find the best hotels in {destination} for a {num_days}-day stay.
        
        Requirements:
        - Budget preference: {budget}
        - Preferred hotel rating: {hotel_rating}
        - Travel theme: {travel_theme or 'General'}
        
        Please provide:
        1. Top 5 hotel recommendations
        2. Hotel names with star ratings
        3. Key amenities (WiFi, pool, gym, etc.)
        4. Approximate price range per night
        5. Location and proximity to attractions
        6. Guest review highlights
        7. Booking suggestions or websites
        
        Format the response in a clear, organized manner with headers and bullet points.
        """
        
        return self.get_response(prompt)
    
    def find_restaurants(self, destination, cuisine_preference=None, budget=None):
        """
        Find restaurants using AI recommendations
        """
        prompt = f"""
        Recommend the best restaurants in {destination}.
        
        Preferences:
        - Cuisine preference: {cuisine_preference or 'Various cuisines'}
        - Budget: {budget or 'All budgets'}
        
        Please provide:
        1. Top 10 restaurant recommendations
        2. Restaurant names with cuisine type
        3. Price range and ratings
        4. Signature dishes or specialties
        5. Location and atmosphere
        6. Reservation requirements
        7. Popular times to visit
        
        Include a mix of local cuisine and international options.
        Format clearly with restaurant names as headers.
        """
        
        return self.get_response(prompt)
    
    def get_travel_tips(self, destination, travel_date=None, duration=None):
        """
        Get general travel tips for a destination
        """
        prompt = f"""
        Provide comprehensive travel tips for {destination}.
        
        Travel details:
        - Travel date: {travel_date or 'Not specified'}
        - Duration: {duration or 'Not specified'}
        
        Please include:
        1. Best time to visit and weather information
        2. Cultural customs and etiquette
        3. Transportation options (airport to city, local transport)
        4. Safety tips and precautions
        5. Currency and tipping guidelines
        6. Must-visit attractions and hidden gems
        7. Local phrases or language tips
        8. Packing recommendations
        9. Emergency contacts and important numbers
        
        Organize the information in clear sections with practical advice.
        """
        
        return self.get_response(prompt)
    
    def compare_destinations(self, destinations_list, travel_purpose=None):
        """
        Compare multiple destinations
        """
        destinations_str = ", ".join(destinations_list)
        
        prompt = f"""
        Compare these travel destinations: {destinations_str}
        
        Travel purpose: {travel_purpose or 'General tourism'}
        
        For each destination, provide:
        1. Best features and attractions
        2. Approximate budget requirements
        3. Ideal trip duration
        4. Best time to visit
        5. Unique experiences offered
        6. Pros and cons
        
        Then provide a recommendation on which destination might be best for different types of travelers.
        Format as a comparison table or clear sections for each destination.
        """
        
        return self.get_response(prompt)
    
    def plan_itinerary(self, destination, duration, interests, budget=None):
        """
        Create a detailed travel itinerary
        """
        prompt = f"""
        Create a detailed {duration}-day itinerary for {destination}.
        
        Traveler interests: {interests}
        Budget: {budget or 'Flexible'}
        
        For each day, provide:
        1. Morning activities (with timing)
        2. Afternoon plans
        3. Evening recommendations
        4. Restaurant suggestions for meals
        5. Transportation between locations
        6. Estimated costs
        7. Alternative options for bad weather
        
        Include practical tips like:
        - Best times to visit attractions
        - Booking requirements
        - Walking distances
        - Local transportation options
        
        Format as Day 1, Day 2, etc. with clear time schedules.
        """
        
        return self.get_response(prompt)