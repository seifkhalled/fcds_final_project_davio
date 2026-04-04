from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from vector_search import search
from ai.orchestrator import TripOrchestrator

app = Flask(__name__)
CORS(app, origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","))

orchestrator = TripOrchestrator()

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", "out")

def parse_budget(budget_str):
    budget_str = budget_str.replace(" EGP", "").replace("+", "-99999")
    parts = budget_str.split("-")
    try:
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return 1000, 2000

def parse_trip_plan_to_json(trip_text):
    result = {
        "overview": "",
        "places": [],
        "restaurants": [],
        "hotels": [],
        "itinerary": [],
        "budget": {
            "accommodation": 0,
            "food": 0,
            "activities": 0,
            "transportation": 0,
            "total": 0,
            "currency": "EGP"
        },
        "tips": []
    }

    sections = re.split(r'##\s+', trip_text)
    
    current_section = None
    current_day = None
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        title = lines[0].strip() if lines else ""
        content = '\n'.join(lines[1:])
        
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ['overview', 'introduction', 'welcome']):
            result["overview"] = content.strip()
            
        elif 'place' in title_lower and 'visit' in title_lower:
            place_pattern = r'\*\*(.+?)\*\*(?:\s*\(([^)]*)\))?'
            for match in re.finditer(place_pattern, content):
                place = {
                    "name": match.group(1).strip(),
                    "city": match.group(2).strip() if match.group(2) else ""
                }
                result["places"].append(place)
                
        elif 'restaurant' in title_lower or 'dining' in title_lower:
            rest_pattern = r'\*\*(.+?)\*\*(?:\s*\(([^)]*)\))?'
            for match in re.finditer(rest_pattern, content):
                restaurant = {
                    "name": match.group(1).strip(),
                    "city": match.group(2).strip() if match.group(2) else ""
                }
                result["restaurants"].append(restaurant)
                
        elif 'hotel' in title_lower or 'accommodation' in title_lower:
            hotel_pattern = r'\*\*(.+?)\*\*(?:\s*\(([^)]*)\))?'
            for match in re.finditer(hotel_pattern, content):
                hotel = {
                    "name": match.group(1).strip(),
                    "city": match.group(2).strip() if match.group(2) else ""
                }
                result["hotels"].append(hotel)
                
        elif 'budget' in title_lower or 'cost' in title_lower:
            amount_match = re.search(r'(\d+)\s*EGP', content)
            if amount_match:
                total = int(amount_match.group(1))
                result["budget"] = {
                    "accommodation": round(total * 0.4),
                    "food": round(total * 0.25),
                    "activities": round(total * 0.2),
                    "transportation": round(total * 0.15),
                    "total": total,
                    "currency": "EGP"
                }
                
        elif 'tip' in title_lower or 'advice' in title_lower or 'note' in title_lower:
            tips = re.findall(r'[-*]\s*(.+)', content)
            result["tips"] = [t.strip() for t in tips if t.strip()]
            
        elif 'day' in title_lower or 'itinerary' in title_lower:
            day_pattern = r'(?:Day\s*(\d+)|\*\*Day\s*(\d+)\*\*)'
            day_matches = list(re.finditer(day_pattern, content, re.IGNORECASE))
            
            for i, match in enumerate(day_matches):
                day_num = int(match.group(1) or match.group(2))
                start = match.end()
                end = day_matches[i + 1].start() if i + 1 < len(day_matches) else len(content)
                day_content = content[start:end]
                
                day_entry = {
                    "day": day_num,
                    "date": "",
                    "morning": None,
                    "lunch": None,
                    "afternoon": None,
                    "dinner": None,
                    "dayCost": ""
                }
                
                activities = re.findall(r'[-*]\s*(.+)', day_content)
                for j, activity in enumerate(activities):
                    activity = activity.strip()
                    if j < 2:
                        day_entry["morning"] = {
                            "place": "Morning Activity",
                            "description": activity
                        }
                    elif j < 4:
                        day_entry["afternoon"] = {
                            "place": "Afternoon Activity",
                            "description": activity
                        }
                
                result["itinerary"].append(day_entry)

    if not result["overview"] and sections:
        result["overview"] = sections[0].strip()
        
    return result

@app.route('/api/trip', methods=['POST'])
def generate_trip():
    try:
        data = request.json
        
        destinations = data.get('destinations', ['Cairo & Giza'])
        budget = data.get('budget', '1000-2000 EGP')
        group_size = data.get('groupSize', 2)
        start_date = data.get('startDate', '')
        end_date = data.get('endDate', '')
        travel_styles = data.get('travelStyles', ['Historical', 'Food & Dining'])
        historical_knowledge = data.get('historicalKnowledge', 'Beginner')
        preferred_time_periods = data.get('preferredTimePeriods', ['Pharaonic', 'Islamic'])
        museum_visits = data.get('museumVisits', True)
        water_activities = data.get('waterActivities', False)
        accommodation_type = data.get('accommodationType', 'Medium')
        transportation = data.get('transportation', 'Private Car')
        food_preferences = data.get('foodPreferences', 'Vegetarian')
        trip_pace = data.get('tripPace', 'Moderate')
        must_visit = data.get('mustVisit', 'Pyramids')

        budget_min, budget_max = parse_budget(budget)

        city_map = {
            "Cairo & Giza": "cairo",
            "Alexandria": "alexandria",
            "Luxor": "luxor",
            "Aswan": "aswan",
            "Sharm El Sheikh": "sharm",
            "Hurghada": "hurghada",
            "Dahab": "dahab",
        }

        query_parts = []

        if "Historical" in travel_styles:
            if "Pharaonic" in preferred_time_periods:
                query_parts.append("pharaonic ancient pyramids temple historical site")
            if "Islamic" in preferred_time_periods:
                query_parts.append("islamic mosque old cairo historic")
            if "Coptic" in preferred_time_periods:
                query_parts.append("coptic church ancient christian")
            if museum_visits:
                query_parts.append("museum exhibition artifacts")
            if historical_knowledge == "Beginner":
                query_parts.append("introductory guided tour overview")

        if "Food & Dining" in travel_styles:
            if food_preferences == "Vegetarian":
                query_parts.append("vegetarian restaurant plant-based food")
            elif food_preferences == "Vegan":
                query_parts.append("vegan restaurant plant-based food")
            else:
                query_parts.append("restaurant local cuisine dining food")

        if "Water Activities" in travel_styles or water_activities:
            query_parts.append("water activities beach diving snorkeling")

        if accommodation_type == "Budget":
            query_parts.append("budget cheap affordable hotel")
        elif accommodation_type == "Medium":
            query_parts.append("mid-range moderate hotel comfortable")
        elif accommodation_type == "Luxury":
            query_parts.append("luxury premium 5-star resort spa")

        if must_visit:
            query_parts.append(must_visit)

        query = " ".join(query_parts) if query_parts else "tourist attractions restaurants hotels"

        results_places = []
        results_restaurants = []
        results_hotels = []

        for city_label in destinations:
            city = city_map.get(city_label, city_label.lower())

            places = search(query=query, entity_type="place", city=city, k=5)
            results_places.extend(places)

            restaurants = search(query=query, entity_type="restaurant", city=city, max_price=budget_max, k=5)
            results_restaurants.extend(restaurants)

            hotels = search(query=query, entity_type="hotel", city=city, max_price=budget_max, k=5)
            results_hotels.extend(hotels)

        try:
            summary = orchestrator.generate_summary(results_places, results_restaurants, results_hotels, destinations)
        except Exception as e:
            summary = f"Your trip to {', '.join(destinations)} is ready!"

        try:
            start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now()
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
        except:
            start_dt = datetime.now()
            end_dt = datetime.now()

        trip_plan_text = orchestrator.generate_trip_plan(
            destinations=destinations,
            budget=budget,
            group_size=group_size,
            start_date=start_dt,
            end_date=end_dt,
            travel_styles=travel_styles,
            historical_knowledge=historical_knowledge,
            preferred_time_periods=preferred_time_periods,
            museum_visits=museum_visits,
            water_activities=water_activities,
            accommodation_type=accommodation_type,
            transportation=transportation,
            food_preferences=food_preferences,
            trip_pace=trip_pace,
            must_visit=must_visit,
            places=results_places,
            restaurants=results_restaurants,
            hotels=results_hotels,
        )

        parsed_plan = parse_trip_plan_to_json(trip_plan_text)

        for place in results_places:
            meta = place.get("metadata", {})
            parsed_place = {
                "name": meta.get("name", place.get("name", "Unknown")),
                "address": meta.get("address", ""),
                "rating": str(meta.get("rating", "")),
                "ticketPrice": str(meta.get("ticket_price", "")),
                "timings": meta.get("timings", ""),
                "city": place.get("city", ""),
            }
            if parsed_place not in parsed_plan["places"]:
                parsed_plan["places"].append(parsed_place)

        for restaurant in results_restaurants:
            meta = restaurant.get("metadata", {})
            parsed_restaurant = {
                "name": meta.get("name", restaurant.get("name", "Unknown")),
                "cuisines": meta.get("cuisines", ""),
                "avgPrice": str(meta.get("avg_price", "")),
                "location": meta.get("location", ""),
                "city": restaurant.get("city", ""),
            }
            if parsed_restaurant not in parsed_plan["restaurants"]:
                parsed_plan["restaurants"].append(parsed_restaurant)

        for hotel in results_hotels:
            meta = hotel.get("metadata", {})
            parsed_hotel = {
                "name": meta.get("name", hotel.get("name", "Unknown")),
                "rating": str(meta.get("rating", "")),
                "price": str(meta.get("price", "")),
                "distanceKm": str(meta.get("distance_km", "")),
                "city": hotel.get("city", ""),
            }
            if parsed_hotel not in parsed_plan["hotels"]:
                parsed_plan["hotels"].append(parsed_hotel)

        if not parsed_plan["overview"]:
            parsed_plan["overview"] = summary

        return jsonify(parsed_plan)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
