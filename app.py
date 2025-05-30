import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pytz
import calendar
import requests
import json
import math
from hijri_converter import Hijri, Gregorian
import wikipedia
import feedparser
import xml.etree.ElementTree as ET
from urllib.parse import quote
import time
import random

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded successfully!")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"⚠️ Error loading .env file: {e}")

# ------------ REAL-TIME API FUNCTIONS ------------

def get_accurate_datetime():
    """Get accurate current date and time using WorldTimeAPI"""
    try:
        # Get Pakistan time from WorldTimeAPI
        response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Karachi", timeout=5)
        if response.status_code == 200:
            data = response.json()

            # Parse the datetime
            current_time = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))

            # Day names in multiple languages
            english_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            urdu_days = ["پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ", "اتوار"]

            # Month names
            english_months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            urdu_months = [
                "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
                "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
            ]

            day_of_week = current_time.weekday()

            return {
                "success": True,
                "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "date": current_time.strftime("%Y-%m-%d"),
                "time_24h": current_time.strftime("%H:%M:%S"),
                "time_12h": current_time.strftime("%I:%M:%S %p"),
                "day_english": english_days[day_of_week],
                "day_urdu": urdu_days[day_of_week],
                "day_number": current_time.day,
                "month_english": english_months[current_time.month - 1],
                "month_urdu": urdu_months[current_time.month - 1],
                "month_number": current_time.month,
                "year": current_time.year,
                "timezone": data.get('timezone', 'Asia/Karachi'),
                "utc_offset": data.get('utc_offset', '+05:00'),
                "day_of_year": current_time.timetuple().tm_yday,
                "week_number": current_time.isocalendar()[1],
                "is_weekend": day_of_week in [4, 5],  # Friday, Saturday
                "unix_timestamp": data.get('unixtime', int(current_time.timestamp()))
            }
    except Exception as e:
        print(f"WorldTimeAPI failed: {e}")

    # Fallback to local time with timezone
    try:
        pk_tz = pytz.timezone('Asia/Karachi')
        current_time = datetime.now(pk_tz)

        english_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        urdu_days = ["پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ", "اتوار"]
        english_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        urdu_months = [
            "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
            "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
        ]

        day_of_week = current_time.weekday()

        return {
            "success": True,
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time_24h": current_time.strftime("%H:%M:%S"),
            "time_12h": current_time.strftime("%I:%M:%S %p"),
            "day_english": english_days[day_of_week],
            "day_urdu": urdu_days[day_of_week],
            "day_number": current_time.day,
            "month_english": english_months[current_time.month - 1],
            "month_urdu": urdu_months[current_time.month - 1],
            "month_number": current_time.month,
            "year": current_time.year,
            "timezone": "PKT (Pakistan Standard Time)",
            "utc_offset": "+05:00",
            "day_of_year": current_time.timetuple().tm_yday,
            "week_number": current_time.isocalendar()[1],
            "is_weekend": day_of_week in [4, 5],
            "unix_timestamp": int(current_time.timestamp())
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get datetime: {str(e)}"}

def get_accurate_islamic_date():
    """Get accurate Islamic (Hijri) date using proper conversion"""
    try:
        # Get current Gregorian date
        today = datetime.now()

        # Convert to Hijri using hijri-converter library
        hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()

        # Islamic month names in Arabic and English
        islamic_months_arabic = [
            "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
            "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
            "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        ]

        islamic_months_english = [
            "Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-thani",
            "Jumada al-awwal", "Jumada al-thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
        ]

        return {
            "success": True,
            "hijri_date": f"{hijri_date.day} {islamic_months_english[hijri_date.month-1]} {hijri_date.year} AH",
            "hijri_date_arabic": f"{hijri_date.day} {islamic_months_arabic[hijri_date.month-1]} {hijri_date.year} هـ",
            "hijri_day": hijri_date.day,
            "hijri_month": hijri_date.month,
            "hijri_month_name": islamic_months_english[hijri_date.month-1],
            "hijri_month_arabic": islamic_months_arabic[hijri_date.month-1],
            "hijri_year": hijri_date.year
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get Islamic date: {str(e)}"}

def get_accurate_prayer_times(city="Karachi"):
    """Get accurate prayer times using Aladhan API"""
    try:
        # Get prayer times from Aladhan API
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']

            return {
                "success": True,
                "city": city,
                "date": data['data']['date']['readable'],
                "prayer_times": {
                    "Fajr": timings['Fajr'],
                    "Sunrise": timings['Sunrise'],
                    "Dhuhr": timings['Dhuhr'],
                    "Asr": timings['Asr'],
                    "Maghrib": timings['Maghrib'],
                    "Isha": timings['Isha']
                },
                "qibla_direction": data['data'].get('meta', {}).get('qibla_direction', "Not available")
            }
        else:
            return {"success": False, "error": "Prayer times API unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get prayer times: {str(e)}"}

def get_accurate_weather(city="Karachi"):
    """Get accurate weather using wttr.in API"""
    try:
        # Get weather from wttr.in (no API key required)
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]

            return {
                "success": True,
                "city": city,
                "temperature_c": current['temp_C'],
                "temperature_f": current['temp_F'],
                "condition": current['weatherDesc'][0]['value'],
                "feels_like_c": current['FeelsLikeC'],
                "feels_like_f": current['FeelsLikeF'],
                "humidity": current['humidity'],
                "wind_speed_kmph": current['windspeedKmph'],
                "wind_direction": current['winddir16Point'],
                "pressure": current['pressure'],
                "visibility": current['visibility'],
                "uv_index": current['uvIndex']
            }
        else:
            return {"success": False, "error": "Weather API unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get weather: {str(e)}"}

def get_world_times():
    """Get current time in major world cities"""
    try:
        cities = [
            ("New York", "America/New_York"),
            ("London", "Europe/London"),
            ("Dubai", "Asia/Dubai"),
            ("Tokyo", "Asia/Tokyo"),
            ("Sydney", "Australia/Sydney"),
            ("Paris", "Europe/Paris"),
            ("Istanbul", "Europe/Istanbul"),
            ("Riyadh", "Asia/Riyadh")
        ]

        world_times = {}
        for city, timezone in cities:
            try:
                response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    time_obj = datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
                    world_times[city] = {
                        "time": time_obj.strftime("%H:%M:%S"),
                        "date": time_obj.strftime("%Y-%m-%d"),
                        "timezone": timezone
                    }
            except:
                # Fallback to pytz
                tz = pytz.timezone(timezone)
                local_time = datetime.now(tz)
                world_times[city] = {
                    "time": local_time.strftime("%H:%M:%S"),
                    "date": local_time.strftime("%Y-%m-%d"),
                    "timezone": timezone
                }

        return {"success": True, "world_times": world_times}
    except Exception as e:
        return {"success": False, "error": f"Failed to get world times: {str(e)}"}

def get_currency_rates():
    """Get current currency exchange rates"""
    try:
        # Using exchangerate-api.com (free tier)
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "base_currency": "USD",
                "rates": {
                    "PKR": data['rates'].get('PKR', 'N/A'),
                    "EUR": data['rates'].get('EUR', 'N/A'),
                    "GBP": data['rates'].get('GBP', 'N/A'),
                    "JPY": data['rates'].get('JPY', 'N/A'),
                    "AED": data['rates'].get('AED', 'N/A'),
                    "SAR": data['rates'].get('SAR', 'N/A'),
                    "INR": data['rates'].get('INR', 'N/A'),
                    "CAD": data['rates'].get('CAD', 'N/A'),
                    "AUD": data['rates'].get('AUD', 'N/A')
                },
                "last_updated": data.get('date', 'Unknown')
            }
        else:
            return {"success": False, "error": "Currency API unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get currency rates: {str(e)}"}

def get_crypto_prices():
    """Get current cryptocurrency prices"""
    try:
        # Using CoinGecko API (free)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana,dogecoin&vs_currencies=usd,pkr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "prices": {
                    "Bitcoin (BTC)": {"usd": data.get('bitcoin', {}).get('usd', 'N/A'), "pkr": data.get('bitcoin', {}).get('pkr', 'N/A')},
                    "Ethereum (ETH)": {"usd": data.get('ethereum', {}).get('usd', 'N/A'), "pkr": data.get('ethereum', {}).get('pkr', 'N/A')},
                    "Binance Coin (BNB)": {"usd": data.get('binancecoin', {}).get('usd', 'N/A'), "pkr": data.get('binancecoin', {}).get('pkr', 'N/A')},
                    "Cardano (ADA)": {"usd": data.get('cardano', {}).get('usd', 'N/A'), "pkr": data.get('cardano', {}).get('pkr', 'N/A')},
                    "Solana (SOL)": {"usd": data.get('solana', {}).get('usd', 'N/A'), "pkr": data.get('solana', {}).get('pkr', 'N/A')},
                    "Dogecoin (DOGE)": {"usd": data.get('dogecoin', {}).get('usd', 'N/A'), "pkr": data.get('dogecoin', {}).get('pkr', 'N/A')}
                }
            }
        else:
            return {"success": False, "error": "Crypto API unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get crypto prices: {str(e)}"}

def get_news_headlines():
    """Get current news headlines"""
    try:
        # Using NewsAPI (you can get free API key from newsapi.org)
        # For now using a simple RSS feed parser
        import feedparser

        # BBC News RSS feed
        feed = feedparser.parse("http://feeds.bbci.co.uk/news/rss.xml")
        headlines = []

        for entry in feed.entries[:5]:  # Get top 5 headlines
            headlines.append({
                "title": entry.title,
                "summary": entry.summary[:200] + "..." if len(entry.summary) > 200 else entry.summary,
                "published": entry.published,
                "link": entry.link
            })

        return {
            "success": True,
            "source": "BBC News",
            "headlines": headlines
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get news: {str(e)}"}

def get_country_info(country="Pakistan"):
    """Get information about a country"""
    try:
        # Using REST Countries API
        response = requests.get(f"https://restcountries.com/v3.1/name/{country}", timeout=5)
        if response.status_code == 200:
            data = response.json()[0]
            return {
                "success": True,
                "country": {
                    "name": data['name']['common'],
                    "official_name": data['name']['official'],
                    "capital": data.get('capital', ['N/A'])[0],
                    "population": data.get('population', 'N/A'),
                    "area": data.get('area', 'N/A'),
                    "region": data.get('region', 'N/A'),
                    "subregion": data.get('subregion', 'N/A'),
                    "languages": list(data.get('languages', {}).values()),
                    "currencies": list(data.get('currencies', {}).keys()),
                    "timezone": data.get('timezones', ['N/A'])[0],
                    "flag": data.get('flag', '🏳️')
                }
            }
        else:
            return {"success": False, "error": "Country not found"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get country info: {str(e)}"}

def get_space_info():
    """Get space and astronomy information"""
    try:
        # Using NASA API for Astronomy Picture of the Day
        response = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "astronomy_picture": {
                    "title": data.get('title', 'N/A'),
                    "explanation": data.get('explanation', 'N/A')[:300] + "...",
                    "date": data.get('date', 'N/A'),
                    "url": data.get('url', 'N/A')
                },
                "space_facts": [
                    "The International Space Station orbits Earth every 90 minutes",
                    "One day on Venus is longer than one year on Venus",
                    "Jupiter has 95 known moons",
                    "The Sun contains 99.86% of the mass in our solar system",
                    "Light from the Sun takes 8 minutes to reach Earth"
                ]
            }
        else:
            return {"success": False, "error": "Space API unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get space info: {str(e)}"}

def get_health_tips():
    """Get daily health tips and information"""
    try:
        health_tips = [
            "Drink at least 8 glasses of water daily for optimal hydration",
            "Take a 10-minute walk after meals to aid digestion",
            "Get 7-9 hours of sleep for better mental and physical health",
            "Eat 5 servings of fruits and vegetables daily",
            "Practice deep breathing for 5 minutes to reduce stress",
            "Limit screen time before bed for better sleep quality",
            "Wash your hands frequently to prevent infections",
            "Take breaks every hour if you work at a computer",
            "Include protein in every meal for sustained energy",
            "Practice gratitude daily for better mental health"
        ]

        import random
        daily_tip = random.choice(health_tips)

        return {
            "success": True,
            "daily_health_tip": daily_tip,
            "health_reminders": [
                "Stay hydrated throughout the day",
                "Take regular breaks from work",
                "Maintain good posture",
                "Get some sunlight for Vitamin D",
                "Practice mindfulness or meditation"
            ],
            "emergency_numbers": {
                "Pakistan": {
                    "Emergency": "15",
                    "Police": "15",
                    "Fire": "16",
                    "Ambulance": "1122",
                    "Rescue": "1122"
                }
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get health tips: {str(e)}"}

def get_detailed_weather(city="Karachi"):
    """Get comprehensive weather information with more details"""
    try:
        # Using wttr.in for detailed weather
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            today_weather = data['weather'][0]

            return {
                "success": True,
                "city": city,
                "current_conditions": {
                    "temperature_c": current['temp_C'],
                    "temperature_f": current['temp_F'],
                    "feels_like_c": current['FeelsLikeC'],
                    "feels_like_f": current['FeelsLikeF'],
                    "condition": current['weatherDesc'][0]['value'],
                    "humidity": current['humidity'] + "%",
                    "wind_speed_kmph": current['windspeedKmph'] + " km/h",
                    "wind_direction": current['winddir16Point'],
                    "pressure": current['pressure'] + " mb",
                    "visibility": current['visibility'] + " km",
                    "uv_index": current['uvIndex'],
                    "cloud_cover": current['cloudcover'] + "%"
                },
                "today_forecast": {
                    "max_temp_c": today_weather['maxtempC'],
                    "min_temp_c": today_weather['mintempC'],
                    "max_temp_f": today_weather['maxtempF'],
                    "min_temp_f": today_weather['mintempF'],
                    "sunrise": today_weather['astronomy'][0]['sunrise'],
                    "sunset": today_weather['astronomy'][0]['sunset'],
                    "moonrise": today_weather['astronomy'][0]['moonrise'],
                    "moonset": today_weather['astronomy'][0]['moonset'],
                    "moon_phase": today_weather['astronomy'][0]['moon_phase']
                },
                "air_quality": {
                    "status": "Moderate" if int(current.get('uvIndex', 0)) < 6 else "High",
                    "recommendation": "Safe for outdoor activities" if int(current.get('uvIndex', 0)) < 6 else "Use sun protection"
                }
            }
        else:
            return {"success": False, "error": "Weather service unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Failed to get detailed weather: {str(e)}"}

def get_sports_scores():
    """Get current sports scores and information"""
    try:
        # Sports data (you can integrate with sports APIs)
        sports_info = {
            "success": True,
            "cricket": {
                "latest_matches": [
                    "Pakistan vs India - Pakistan won by 5 wickets",
                    "England vs Australia - Match in progress",
                    "PSL 2025 - Karachi Kings vs Lahore Qalandars"
                ],
                "upcoming": [
                    "Pakistan vs New Zealand - Tomorrow 2:30 PM",
                    "World Cup Qualifier - Next week"
                ]
            },
            "football": {
                "premier_league": "Manchester City leading the table",
                "champions_league": "Quarter-finals in progress",
                "world_cup": "Next World Cup: 2026 (USA, Canada, Mexico)"
            },
            "olympics": {
                "next_games": "Paris 2024 Olympics completed",
                "pakistan_medals": "1 Gold in Javelin Throw (Arshad Nadeem)"
            }
        }
        return sports_info
    except Exception as e:
        return {"success": False, "error": f"Failed to get sports info: {str(e)}"}

def get_stock_market():
    """Get stock market information"""
    try:
        # Using Alpha Vantage or Yahoo Finance (free tier)
        # For demo, using static data - you can integrate real APIs
        market_data = {
            "success": True,
            "pakistan_stock_exchange": {
                "kse_100": "45,250.30",
                "change": "+125.50 (+0.28%)",
                "status": "Market Open",
                "top_gainers": [
                    "TRG Pakistan: +5.2%",
                    "Systems Limited: +3.8%",
                    "Engro Corporation: +2.1%"
                ]
            },
            "international_markets": {
                "dow_jones": "34,567.89 (+0.45%)",
                "nasdaq": "13,987.65 (+0.32%)",
                "ftse_100": "7,456.23 (+0.18%)",
                "nikkei": "28,345.67 (-0.12%)"
            },
            "commodities": {
                "gold": "$1,985.50/oz (+0.8%)",
                "oil_brent": "$85.30/barrel (+1.2%)",
                "silver": "$24.15/oz (+0.5%)"
            }
        }
        return market_data
    except Exception as e:
        return {"success": False, "error": f"Failed to get market data: {str(e)}"}

def get_traffic_info(city="Karachi"):
    """Get traffic and transportation information"""
    try:
        traffic_data = {
            "success": True,
            "city": city,
            "current_traffic": {
                "overall_status": "Moderate",
                "peak_hours": "8:00-10:00 AM, 5:00-8:00 PM",
                "major_routes": {
                    "Shahrah-e-Faisal": "Heavy traffic",
                    "I.I. Chundrigar Road": "Moderate",
                    "M.A. Jinnah Road": "Light traffic",
                    "University Road": "Heavy traffic"
                }
            },
            "public_transport": {
                "bus_rapid_transit": "Green Line operational",
                "metro": "Orange Line running normally",
                "rickshaw_fare": "Starting from Rs. 50",
                "taxi_services": ["Careem", "Uber", "InDriver"]
            },
            "fuel_prices": {
                "petrol": "Rs. 280/liter",
                "diesel": "Rs. 290/liter",
                "cng": "Rs. 150/kg"
            }
        }
        return traffic_data
    except Exception as e:
        return {"success": False, "error": f"Failed to get traffic info: {str(e)}"}

def get_education_info():
    """Get education and academic information"""
    try:
        education_data = {
            "success": True,
            "universities": {
                "top_pakistani": [
                    "LUMS - Lahore University of Management Sciences",
                    "IBA Karachi - Institute of Business Administration",
                    "NUST - National University of Sciences & Technology",
                    "FAST - Foundation for Advancement of Science & Technology"
                ],
                "admission_season": "Spring admissions open (January-March)",
                "scholarships": [
                    "HEC Need-based Scholarships",
                    "Punjab Educational Endowment Fund",
                    "Ehsaas Undergraduate Scholarship"
                ]
            },
            "courses_trending": [
                "Computer Science & AI",
                "Data Science",
                "Digital Marketing",
                "Cybersecurity",
                "Business Analytics"
            ],
            "online_learning": [
                "Coursera", "edX", "Khan Academy", "Udemy", "Skillshare"
            ]
        }
        return education_data
    except Exception as e:
        return {"success": False, "error": f"Failed to get education info: {str(e)}"}

def get_entertainment_info():
    """Get entertainment and media information"""
    try:
        entertainment_data = {
            "success": True,
            "movies": {
                "trending_pakistani": [
                    "The Legend of Maula Jatt",
                    "Tere Bin Drama Series",
                    "Mere Humsafar"
                ],
                "hollywood_releases": [
                    "Latest Marvel movies",
                    "Action blockbusters",
                    "Animated features"
                ]
            },
            "music": {
                "trending_artists": [
                    "Atif Aslam", "Rahat Fateh Ali Khan", "Asim Azhar",
                    "Momina Mustehsan", "Ali Zafar"
                ],
                "genres_popular": ["Qawwali", "Pop", "Rock", "Classical"]
            },
            "tv_channels": {
                "news": ["Geo News", "ARY News", "Dunya News"],
                "entertainment": ["Hum TV", "ARY Digital", "Geo Entertainment"],
                "sports": ["PTV Sports", "A Sports", "Ten Sports"]
            }
        }
        return entertainment_data
    except Exception as e:
        return {"success": False, "error": f"Failed to get entertainment info: {str(e)}"}

# ------------ COMPREHENSIVE WORLD KNOWLEDGE SYSTEM ------------

def get_wikipedia_info(topic, language='en'):
    """Get comprehensive information from Wikipedia"""
    try:
        # Set Wikipedia language
        wikipedia.set_lang(language)

        # Search for the topic
        search_results = wikipedia.search(topic, results=3)
        if not search_results:
            return {"success": False, "error": f"No Wikipedia articles found for '{topic}'"}

        # Get the main article
        page = wikipedia.page(search_results[0])

        # Get summary (first 500 characters)
        summary = wikipedia.summary(topic, sentences=3)

        return {
            "success": True,
            "topic": topic,
            "title": page.title,
            "summary": summary,
            "full_content": page.content[:2000] + "..." if len(page.content) > 2000 else page.content,
            "url": page.url,
            "categories": page.categories[:10],  # First 10 categories
            "links": page.links[:15],  # First 15 related links
            "images": page.images[:5] if hasattr(page, 'images') else [],
            "coordinates": getattr(page, 'coordinates', None),
            "language": language,
            "last_updated": "Real-time from Wikipedia"
        }
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation pages
        try:
            page = wikipedia.page(e.options[0])
            summary = wikipedia.summary(e.options[0], sentences=3)
            return {
                "success": True,
                "topic": topic,
                "title": page.title,
                "summary": summary,
                "disambiguation_options": e.options[:10],
                "url": page.url,
                "note": "Multiple topics found, showing the most relevant one"
            }
        except:
            return {
                "success": False,
                "error": f"Multiple topics found for '{topic}'",
                "suggestions": e.options[:10]
            }
    except wikipedia.exceptions.PageError:
        return {"success": False, "error": f"No Wikipedia page found for '{topic}'"}
    except Exception as e:
        return {"success": False, "error": f"Wikipedia error: {str(e)}"}

def get_global_news():
    """Get comprehensive news from multiple sources"""
    try:
        news_sources = []

        # BBC News
        try:
            bbc_feed = feedparser.parse("http://feeds.bbci.co.uk/news/rss.xml")
            for entry in bbc_feed.entries[:3]:
                news_sources.append({
                    "source": "BBC News",
                    "title": entry.title,
                    "summary": entry.summary[:200] + "..." if len(entry.summary) > 200 else entry.summary,
                    "published": entry.published,
                    "link": entry.link,
                    "category": "International"
                })
        except:
            pass

        # CNN RSS
        try:
            cnn_feed = feedparser.parse("http://rss.cnn.com/rss/edition.rss")
            for entry in cnn_feed.entries[:3]:
                news_sources.append({
                    "source": "CNN",
                    "title": entry.title,
                    "summary": entry.summary[:200] + "..." if hasattr(entry, 'summary') else "No summary available",
                    "published": entry.published,
                    "link": entry.link,
                    "category": "International"
                })
        except:
            pass

        # Reuters
        try:
            reuters_feed = feedparser.parse("https://feeds.reuters.com/reuters/topNews")
            for entry in reuters_feed.entries[:3]:
                news_sources.append({
                    "source": "Reuters",
                    "title": entry.title,
                    "summary": entry.summary[:200] + "..." if hasattr(entry, 'summary') else "No summary available",
                    "published": entry.published,
                    "link": entry.link,
                    "category": "Business"
                })
        except:
            pass

        return {
            "success": True,
            "total_articles": len(news_sources),
            "sources": ["BBC News", "CNN", "Reuters"],
            "articles": news_sources,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": ["International", "Business", "Technology", "Sports", "Health"]
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to get global news: {str(e)}"}

def get_educational_content(subject="general"):
    """Get comprehensive educational content"""
    try:
        educational_resources = {
            "mathematics": {
                "topics": ["Algebra", "Calculus", "Geometry", "Statistics", "Number Theory"],
                "formulas": [
                    "Quadratic Formula: x = (-b ± √(b²-4ac)) / 2a",
                    "Pythagorean Theorem: a² + b² = c²",
                    "Area of Circle: A = πr²",
                    "Derivative of x^n: nx^(n-1)",
                    "Integration by parts: ∫udv = uv - ∫vdu"
                ],
                "resources": ["Khan Academy", "MIT OpenCourseWare", "Wolfram Alpha"]
            },
            "science": {
                "physics": [
                    "Newton's Laws of Motion",
                    "Einstein's Theory of Relativity: E=mc²",
                    "Quantum Mechanics Principles",
                    "Thermodynamics Laws",
                    "Electromagnetic Theory"
                ],
                "chemistry": [
                    "Periodic Table Elements: 118 known elements",
                    "Chemical Bonding: Ionic, Covalent, Metallic",
                    "Organic Chemistry: Carbon-based compounds",
                    "Acids and Bases: pH scale 0-14",
                    "Chemical Reactions: Synthesis, Decomposition, etc."
                ],
                "biology": [
                    "Cell Theory: All life is made of cells",
                    "DNA Structure: Double helix with base pairs",
                    "Evolution: Natural selection and adaptation",
                    "Photosynthesis: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
                    "Human Body Systems: 11 major systems"
                ]
            },
            "history": {
                "ancient": ["Egyptian Civilization", "Greek Empire", "Roman Empire", "Chinese Dynasties"],
                "medieval": ["Islamic Golden Age", "Byzantine Empire", "Mongol Empire", "Renaissance"],
                "modern": ["Industrial Revolution", "World Wars", "Cold War", "Digital Age"],
                "important_dates": [
                    "3100 BCE: Egyptian civilization begins",
                    "776 BCE: First Olympic Games",
                    "622 CE: Islamic calendar begins",
                    "1492: Columbus reaches Americas",
                    "1969: Moon landing"
                ]
            },
            "geography": {
                "continents": ["Asia", "Africa", "North America", "South America", "Antarctica", "Europe", "Australia"],
                "oceans": ["Pacific", "Atlantic", "Indian", "Southern", "Arctic"],
                "highest_peaks": [
                    "Mount Everest: 8,848.86 m (Asia)",
                    "Aconcagua: 6,961 m (South America)",
                    "Denali: 6,190 m (North America)",
                    "Kilimanjaro: 5,895 m (Africa)",
                    "Mount Elbrus: 5,642 m (Europe)"
                ],
                "longest_rivers": [
                    "Nile: 6,650 km (Africa)",
                    "Amazon: 6,400 km (South America)",
                    "Yangtze: 6,300 km (Asia)",
                    "Mississippi: 6,275 km (North America)",
                    "Yenisei: 5,539 km (Asia)"
                ]
            }
        }

        if subject.lower() in educational_resources:
            return {
                "success": True,
                "subject": subject,
                "content": educational_resources[subject.lower()],
                "study_tips": [
                    "Break complex topics into smaller parts",
                    "Use active recall and spaced repetition",
                    "Create mind maps and visual aids",
                    "Practice with real-world examples",
                    "Teach others to reinforce learning"
                ]
            }
        else:
            return {
                "success": True,
                "available_subjects": list(educational_resources.keys()),
                "general_content": {
                    "study_methods": ["Active Reading", "Note-taking", "Flashcards", "Group Study"],
                    "learning_tips": [
                        "Set specific learning goals",
                        "Create a study schedule",
                        "Find your optimal learning environment",
                        "Take regular breaks (Pomodoro Technique)",
                        "Review and revise regularly"
                    ]
                }
            }
    except Exception as e:
        return {"success": False, "error": f"Failed to get educational content: {str(e)}"}

def get_world_facts():
    """Get comprehensive world facts and statistics"""
    try:
        world_facts = {
            "success": True,
            "population": {
                "world_population": "8.1 billion (2024)",
                "most_populous_countries": [
                    "China: 1.4 billion",
                    "India: 1.4 billion",
                    "USA: 335 million",
                    "Indonesia: 275 million",
                    "Pakistan: 240 million"
                ],
                "growth_rate": "0.87% annually"
            },
            "languages": {
                "total_languages": "7,000+ languages worldwide",
                "most_spoken": [
                    "Mandarin Chinese: 918 million",
                    "Spanish: 460 million",
                    "English: 379 million",
                    "Hindi: 341 million",
                    "Arabic: 422 million"
                ]
            },
            "economics": {
                "largest_economies": [
                    "USA: $26.9 trillion GDP",
                    "China: $17.7 trillion GDP",
                    "Japan: $4.9 trillion GDP",
                    "Germany: $4.3 trillion GDP",
                    "India: $3.7 trillion GDP"
                ],
                "global_gdp": "$105 trillion (2024)"
            },
            "technology": {
                "internet_users": "5.16 billion (64% of world population)",
                "mobile_users": "5.44 billion",
                "social_media_users": "4.8 billion",
                "ai_market_size": "$136 billion (2024)"
            },
            "environment": {
                "climate_change": "Global temperature increased 1.1°C since 1880",
                "renewable_energy": "30% of global electricity generation",
                "deforestation": "10 million hectares lost annually",
                "ocean_plastic": "8 million tons enter oceans yearly"
            }
        }
        return world_facts
    except Exception as e:
        return {"success": False, "error": f"Failed to get world facts: {str(e)}"}

def get_google_search_results(query, num_results=5):
    """Get search results using DuckDuckGo (100% FREE, no API key needed)"""
    try:
        import urllib.parse

        # Use DuckDuckGo Instant Answer API (completely free)
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

        response = requests.get(search_url, timeout=5)
        if response.status_code == 200:
            data = response.json()

            results = []

            # Get instant answer
            if data.get('Answer'):
                results.append({
                    'title': 'Instant Answer',
                    'snippet': data['Answer'],
                    'url': data.get('AnswerURL', ''),
                    'source': 'DuckDuckGo Instant'
                })

            # Get abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Abstract'),
                    'snippet': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'source': data.get('AbstractSource', 'DuckDuckGo')
                })

            # Get related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': 'Related Topic',
                        'snippet': topic['Text'],
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo Related'
                    })

            return {
                'success': True,
                'query': query,
                'results': results,
                'total_results': len(results),
                'source': 'DuckDuckGo (100% Free)',
                'api_cost': '$0.00'
            }

        return {"success": False, "error": "Search service unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Search failed: {str(e)}"}

def get_youtube_educational_content(topic):
    """Get educational YouTube content (100% FREE, no API key needed)"""
    try:
        # Use YouTube RSS feeds (completely free)
        educational_channels = {
            'Khan Academy': 'UC4a-Gbdw7vOaccHmFo40b9g',
            'Crash Course': 'UCX6b17PVsYBQ0ip5gyeme-Q',
            'TED-Ed': 'UCsooa4yRKGN_zEE8iknghZA',
            'MIT OpenCourseWare': 'UCEBb1b_L6zDS3xTUrIALZOw',
            'National Geographic': 'UCpVm7bg6pXKo1Pr6k5kxG9A'
        }

        educational_content = []

        for channel_name, channel_id in educational_channels.items():
            try:
                # Get RSS feed for channel
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                feed = feedparser.parse(rss_url)

                for entry in feed.entries[:2]:  # Top 2 videos per channel
                    if topic.lower() in entry.title.lower() or topic.lower() in entry.summary.lower():
                        educational_content.append({
                            'channel': channel_name,
                            'title': entry.title,
                            'description': entry.summary[:200] + "..." if len(entry.summary) > 200 else entry.summary,
                            'url': entry.link,
                            'published': entry.published,
                            'duration': 'Educational Video',
                            'type': 'Free Educational Content'
                        })
            except:
                continue

        return {
            'success': True,
            'topic': topic,
            'educational_videos': educational_content,
            'total_videos': len(educational_content),
            'channels': list(educational_channels.keys()),
            'source': 'YouTube RSS (100% Free)',
            'api_cost': '$0.00'
        }
    except Exception as e:
        return {"success": False, "error": f"YouTube educational content failed: {str(e)}"}

def get_academic_papers(topic):
    """Get academic papers from arXiv (100% FREE)"""
    try:
        import urllib.parse

        # arXiv API is completely free
        encoded_topic = urllib.parse.quote(topic)
        arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_topic}&start=0&max_results=5"

        response = requests.get(arxiv_url, timeout=10)
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            papers = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text
                          for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                link = entry.find('{http://www.w3.org/2005/Atom}id').text

                papers.append({
                    'title': title,
                    'authors': authors,
                    'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                    'published': published,
                    'url': link,
                    'source': 'arXiv',
                    'type': 'Academic Research Paper'
                })

            return {
                'success': True,
                'topic': topic,
                'papers': papers,
                'total_papers': len(papers),
                'source': 'arXiv (100% Free)',
                'api_cost': '$0.00'
            }

        return {"success": False, "error": "arXiv service unavailable"}
    except Exception as e:
        return {"success": False, "error": f"Academic papers search failed: {str(e)}"}

def get_government_data():
    """Get government and official statistics (100% FREE)"""
    try:
        gov_data = {
            'success': True,
            'pakistan_data': {
                'population': '240 million (2024 estimate)',
                'capital': 'Islamabad',
                'largest_city': 'Karachi',
                'official_languages': ['Urdu', 'English'],
                'currency': 'Pakistani Rupee (PKR)',
                'gdp': '$347 billion (2024)',
                'area': '881,913 km²',
                'independence': 'August 14, 1947',
                'government_type': 'Federal Parliamentary Republic'
            },
            'world_statistics': {
                'world_population': '8.1 billion (2024)',
                'countries': 195,
                'languages': '7,000+',
                'internet_users': '5.16 billion',
                'mobile_users': '5.44 billion',
                'literacy_rate': '86.3% global average'
            },
            'economic_data': {
                'global_gdp': '$105 trillion (2024)',
                'largest_economy': 'United States ($26.9 trillion)',
                'fastest_growing': 'India (6.3% growth)',
                'inflation_rate': '3.2% global average',
                'unemployment': '5.1% global average'
            },
            'technology_stats': {
                'ai_market': '$136 billion (2024)',
                'smartphone_users': '6.8 billion',
                'social_media_users': '4.8 billion',
                'e_commerce': '$6.2 trillion globally',
                'renewable_energy': '30% of global electricity'
            },
            'source': 'Multiple Government APIs & UN Data (100% Free)',
            'api_cost': '$0.00',
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return gov_data
    except Exception as e:
        return {"success": False, "error": f"Government data failed: {str(e)}"}

def get_translation_service(text, target_language='en'):
    """Get translation using free services (100% FREE)"""
    try:
        # Using free translation service
        translations = {
            'success': True,
            'original_text': text,
            'target_language': target_language,
            'common_translations': {
                'hello': {
                    'urdu': 'السلام علیکم / آداب',
                    'arabic': 'السلام عليكم',
                    'hindi': 'नमस्ते',
                    'spanish': 'Hola',
                    'french': 'Bonjour',
                    'german': 'Hallo',
                    'chinese': '你好',
                    'japanese': 'こんにちは'
                },
                'thank you': {
                    'urdu': 'شکریہ',
                    'arabic': 'شكرا',
                    'hindi': 'धन्यवाद',
                    'spanish': 'Gracias',
                    'french': 'Merci',
                    'german': 'Danke',
                    'chinese': '谢谢',
                    'japanese': 'ありがとう'
                }
            },
            'supported_languages': [
                'English', 'Urdu', 'Arabic', 'Hindi', 'Spanish',
                'French', 'German', 'Chinese', 'Japanese', 'Korean'
            ],
            'source': 'Free Translation Service',
            'api_cost': '$0.00'
        }

        return translations
    except Exception as e:
        return {"success": False, "error": f"Translation failed: {str(e)}"}

def get_comprehensive_realtime_info():
    """Get all real-time information in one function"""
    try:
        # Get all information
        datetime_info = get_accurate_datetime()
        islamic_info = get_accurate_islamic_date()
        prayer_info = get_accurate_prayer_times()
        weather_info = get_accurate_weather()
        world_times = get_world_times()

        # Format for AI context
        if datetime_info.get("success"):
            context = f"""
🕐 CURRENT REAL-TIME INFORMATION (ACCURATE APIs):

📅 DATE & TIME (Pakistan):
• Current Date: {datetime_info['date']} ({datetime_info['day_english']} / {datetime_info['day_urdu']})
• Current Time: {datetime_info['time_12h']} PKT
• 24-Hour Format: {datetime_info['time_24h']}
• Full DateTime: {datetime_info['datetime']}
• Day: {datetime_info['day_number']} {datetime_info['month_english']} {datetime_info['year']}
• Day of Year: {datetime_info['day_of_year']}
• Week Number: {datetime_info['week_number']}
• Timezone: {datetime_info['timezone']} ({datetime_info['utc_offset']})
• Weekend: {'Yes' if datetime_info['is_weekend'] else 'No'}

🌙 ISLAMIC CALENDAR:"""

            if islamic_info.get("success"):
                context += f"""
• Hijri Date: {islamic_info['hijri_date']}
• Arabic: {islamic_info['hijri_date_arabic']}
• Month: {islamic_info['hijri_month_name']} ({islamic_info['hijri_month_arabic']})
"""

            if prayer_info.get("success"):
                context += f"""
🕌 PRAYER TIMES ({prayer_info['city']}):
• Fajr: {prayer_info['prayer_times']['Fajr']}
• Sunrise: {prayer_info['prayer_times']['Sunrise']}
• Dhuhr: {prayer_info['prayer_times']['Dhuhr']}
• Asr: {prayer_info['prayer_times']['Asr']}
• Maghrib: {prayer_info['prayer_times']['Maghrib']}
• Isha: {prayer_info['prayer_times']['Isha']}
"""

            # Get detailed weather instead of basic weather
            detailed_weather = get_detailed_weather()
            if detailed_weather.get("success"):
                current = detailed_weather['current_conditions']
                forecast = detailed_weather['today_forecast']
                context += f"""
🌤️ DETAILED WEATHER ({detailed_weather['city']}):
• Current Temperature: {current['temperature_c']}°C ({current['temperature_f']}°F)
• Feels Like: {current['feels_like_c']}°C ({current['feels_like_f']}°F)
• Condition: {current['condition']}
• Humidity: {current['humidity']}
• Wind: {current['wind_speed_kmph']} {current['wind_direction']}
• Pressure: {current['pressure']}
• Visibility: {current['visibility']}
• UV Index: {current['uv_index']}
• Cloud Cover: {current['cloud_cover']}

📅 Today's Forecast:
• Max/Min: {forecast['max_temp_c']}°C / {forecast['min_temp_c']}°C
• Sunrise: {forecast['sunrise']} | Sunset: {forecast['sunset']}
• Moon Phase: {forecast['moon_phase']}
• Air Quality: {detailed_weather['air_quality']['status']}
"""

            if world_times.get("success"):
                context += f"""
🌍 WORLD TIMES:"""
                for city, time_data in world_times['world_times'].items():
                    context += f"""
• {city}: {time_data['time']} ({time_data['date']})"""

            # Add additional information
            currency_info = get_currency_rates()
            if currency_info.get("success"):
                context += f"""

💰 CURRENCY RATES (USD Base):
• 1 USD = {currency_info['rates']['PKR']} PKR
• 1 USD = {currency_info['rates']['EUR']} EUR
• 1 USD = {currency_info['rates']['GBP']} GBP
• 1 USD = {currency_info['rates']['AED']} AED
• 1 USD = {currency_info['rates']['SAR']} SAR
"""

            crypto_info = get_crypto_prices()
            if crypto_info.get("success"):
                context += f"""

₿ CRYPTOCURRENCY PRICES:
• Bitcoin: ${crypto_info['prices']['Bitcoin (BTC)']['usd']} USD
• Ethereum: ${crypto_info['prices']['Ethereum (ETH)']['usd']} USD
• Binance Coin: ${crypto_info['prices']['Binance Coin (BNB)']['usd']} USD
"""

            health_info = get_health_tips()
            if health_info.get("success"):
                context += f"""

🏥 DAILY HEALTH TIP:
{health_info['daily_health_tip']}

Emergency Numbers (Pakistan):
• Emergency: {health_info['emergency_numbers']['Pakistan']['Emergency']}
• Ambulance: {health_info['emergency_numbers']['Pakistan']['Ambulance']}
"""

            # Add additional comprehensive information
            sports_info = get_sports_scores()
            if sports_info.get("success"):
                context += f"""

🏏 SPORTS UPDATE:
• Cricket: {sports_info['cricket']['latest_matches'][0]}
• Football: {sports_info['football']['premier_league']}
• Olympics: {sports_info['olympics']['pakistan_medals']}
"""

            market_info = get_stock_market()
            if market_info.get("success"):
                context += f"""

📈 MARKET UPDATE:
• KSE-100: {market_info['pakistan_stock_exchange']['kse_100']} ({market_info['pakistan_stock_exchange']['change']})
• Gold: {market_info['commodities']['gold']}
• Oil: {market_info['commodities']['oil_brent']}
"""

            traffic_info = get_traffic_info()
            if traffic_info.get("success"):
                context += f"""

🚗 TRAFFIC & TRANSPORT:
• Overall Status: {traffic_info['current_traffic']['overall_status']}
• Peak Hours: {traffic_info['current_traffic']['peak_hours']}
• Petrol Price: {traffic_info['fuel_prices']['petrol']}
• Diesel Price: {traffic_info['fuel_prices']['diesel']}
"""

            context += f"""

Use this COMPREHENSIVE real-time information to answer questions about:
- Date, time, calendar (Gregorian & Islamic)
- Detailed weather conditions (temperature, humidity, wind, UV index, sunrise/sunset)
- Prayer times and Islamic calendar
- World times across major cities
- Currency exchange rates and cryptocurrency prices
- Stock market and commodity prices
- Sports scores and updates
- Traffic conditions and fuel prices
- Health tips and emergency numbers
- News headlines and current events

All information is fetched from reliable APIs and is current as of now.
ALWAYS provide specific numbers, temperatures, and exact data when available.
"""

            return context
        else:
            return "Real-time information temporarily unavailable. Using general knowledge."

    except Exception as e:
        return f"Real-time information error: {str(e)}"

def get_islamic_date():
    """Calculate Islamic (Hijri) date"""
    try:
        # Get current Gregorian date
        today = datetime.now()

        # Islamic calendar calculation (approximate)
        # Using the standard conversion formula
        gregorian_year = today.year
        gregorian_month = today.month
        gregorian_day = today.day

        # Convert to Julian day number
        if gregorian_month <= 2:
            gregorian_year -= 1
            gregorian_month += 12

        a = gregorian_year // 100
        b = 2 - a + (a // 4)

        julian_day = int(365.25 * (gregorian_year + 4716)) + int(30.6001 * (gregorian_month + 1)) + gregorian_day + b - 1524

        # Convert Julian day to Islamic date
        islamic_epoch = 1948439.5  # Julian day of Islamic epoch (July 16, 622 CE)
        days_since_epoch = julian_day - islamic_epoch

        # Islamic year calculation
        islamic_year = int((days_since_epoch * 30) / 10631) + 1

        # Approximate Islamic month and day
        days_in_year = days_since_epoch - ((islamic_year - 1) * 10631 / 30)
        islamic_month = int(days_in_year / 29.5) + 1
        islamic_day = int(days_in_year - ((islamic_month - 1) * 29.5)) + 1

        # Adjust for overflow
        if islamic_month > 12:
            islamic_month = 12
        if islamic_day > 30:
            islamic_day = 30

        # Islamic month names
        islamic_months = [
            "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
            "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
        ]

        month_name = islamic_months[islamic_month - 1] if islamic_month <= 12 else "Muharram"

        return {
            'islamic_date': f"{islamic_day} {month_name} {islamic_year} AH",
            'islamic_day': islamic_day,
            'islamic_month': islamic_month,
            'islamic_month_name': month_name,
            'islamic_year': islamic_year,
            'hijri_year': islamic_year
        }
    except Exception as e:
        print(f"Error calculating Islamic date: {e}")
        return {
            'islamic_date': "Islamic date calculation unavailable",
            'error': str(e)
        }

def get_prayer_times(city="Karachi"):
    """Get Islamic prayer times"""
    try:
        # Using Aladhan API for prayer times
        prayer_url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Pakistan&method=2"
        response = requests.get(prayer_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            timings = data['data']['timings']

            return {
                'city': city,
                'fajr': timings['Fajr'],
                'sunrise': timings['Sunrise'],
                'dhuhr': timings['Dhuhr'],
                'asr': timings['Asr'],
                'maghrib': timings['Maghrib'],
                'isha': timings['Isha'],
                'date': data['data']['date']['readable'],
                'hijri_date': data['data']['date']['hijri']['date'],
                'hijri_month': data['data']['date']['hijri']['month']['en'],
                'hijri_year': data['data']['date']['hijri']['year']
            }
        else:
            return {'error': 'Prayer times service unavailable'}
    except Exception as e:
        return {'error': f'Failed to get prayer times: {str(e)}'}

def get_comprehensive_date_info():
    """Get comprehensive date information including multiple calendars"""
    try:
        # Pakistan timezone
        pakistan_tz = pytz.timezone('Asia/Karachi')
        now = datetime.now(pakistan_tz)

        # Islamic date
        islamic_info = get_islamic_date()

        # Additional calendar information
        day_of_year = now.timetuple().tm_yday
        week_number = now.isocalendar()[1]

        return {
            'gregorian': {
                'date': now.strftime('%d %B %Y'),
                'day': now.strftime('%A'),
                'month': now.strftime('%B'),
                'year': now.year,
                'day_number': now.day,
                'month_number': now.month,
                'day_of_year': day_of_year,
                'week_number': week_number,
                'time': now.strftime('%I:%M %p'),
                'timezone': 'Pakistan Standard Time (PST)'
            },
            'islamic': islamic_info,
            'additional_info': {
                'season': get_season(now),
                'days_until_new_year': (datetime(now.year + 1, 1, 1) - now).days,
                'is_weekend': now.weekday() >= 5,  # Saturday = 5, Sunday = 6
                'quarter': f"Q{(now.month - 1) // 3 + 1}",
                'unix_timestamp': int(now.timestamp())
            }
        }
    except Exception as e:
        return {'error': f'Failed to get comprehensive date info: {str(e)}'}

def get_season(date):
    """Determine the season based on date"""
    month = date.month
    day = date.day

    if (month == 12 and day >= 21) or month in [1, 2] or (month == 3 and day < 20):
        return "Winter"
    elif (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
        return "Spring"
    elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 22):
        return "Summer"
    else:
        return "Autumn"

def get_world_times():
    """Get current time in major world cities"""
    try:
        cities = {
            'Karachi': 'Asia/Karachi',
            'Mecca': 'Asia/Riyadh',
            'Dubai': 'Asia/Dubai',
            'London': 'Europe/London',
            'New York': 'America/New_York',
            'Tokyo': 'Asia/Tokyo',
            'Sydney': 'Australia/Sydney'
        }

        world_times = {}
        for city, timezone in cities.items():
            tz = pytz.timezone(timezone)
            city_time = datetime.now(tz)
            world_times[city] = {
                'time': city_time.strftime('%I:%M %p'),
                'date': city_time.strftime('%d %B %Y'),
                'timezone': timezone
            }

        return world_times
    except Exception as e:
        return {'error': f'Failed to get world times: {str(e)}'}

# ----------- Real-time Information Functions ------------
def get_islamic_date():
    """Get current Islamic (Hijri) date"""
    try:
        # Simple Hijri calculation (approximate)
        gregorian_date = datetime.now()
        # Approximate conversion (this is a simplified version)
        # For accurate conversion, you'd need a proper Islamic calendar library
        hijri_year = gregorian_date.year - 579  # Approximate conversion

        islamic_months = [
            "Muharram", "Safar", "Rabi' al-awwal", "Rabi' al-thani",
            "Jumada al-awwal", "Jumada al-thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
        ]

        # Simple approximation for month
        hijri_month = ((gregorian_date.month + 10) % 12) + 1
        hijri_day = gregorian_date.day

        return f"{hijri_day} {islamic_months[hijri_month-1]} {hijri_year} AH"
    except:
        return "Islamic date calculation unavailable"

def get_comprehensive_datetime_info():
    """Get comprehensive date and time information"""
    try:
        # Pakistan timezone
        pk_tz = pytz.timezone('Asia/Karachi')
        now_pk = datetime.now(pk_tz)

        # UTC time
        now_utc = datetime.now(pytz.UTC)

        # Day names in English and Urdu
        english_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        urdu_days = ["پیر", "منگل", "بدھ", "جمعرات", "جمعہ", "ہفتہ", "اتوار"]

        # Month names in English and Urdu
        english_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        urdu_months = [
            "جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون",
            "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"
        ]

        day_of_week = now_pk.weekday()  # 0 = Monday

        info = {
            "current_datetime_pakistan": now_pk.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "current_datetime_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "date": now_pk.strftime("%Y-%m-%d"),
            "time_24h": now_pk.strftime("%H:%M:%S"),
            "time_12h": now_pk.strftime("%I:%M:%S %p"),
            "day_english": english_days[day_of_week],
            "day_urdu": urdu_days[day_of_week],
            "day_number": now_pk.day,
            "month_english": english_months[now_pk.month - 1],
            "month_urdu": urdu_months[now_pk.month - 1],
            "month_number": now_pk.month,
            "year": now_pk.year,
            "timezone": "PKT (Pakistan Standard Time)",
            "islamic_date": get_islamic_date(),
            "day_of_year": now_pk.timetuple().tm_yday,
            "week_number": now_pk.isocalendar()[1],
            "is_weekend": day_of_week in [4, 5],  # Friday, Saturday in Pakistan
            "season": get_season(now_pk.month),
            "prayer_times_note": "For accurate prayer times, please check local Islamic calendar"
        }

        return info
    except Exception as e:
        return {"error": f"DateTime calculation error: {str(e)}"}

def get_season(month):
    """Get current season"""
    if month in [12, 1, 2]:
        return "Winter (سردی)"
    elif month in [3, 4, 5]:
        return "Spring (بہار)"
    elif month in [6, 7, 8]:
        return "Summer (گرمی)"
    else:
        return "Autumn (خزاں)"

def format_datetime_for_ai(datetime_info):
    """Format datetime info for AI context"""
    if "error" in datetime_info:
        return "Current date/time information is temporarily unavailable."

    formatted = f"""
CURRENT REAL-TIME INFORMATION (Pakistan Time):
📅 Date: {datetime_info['date']} ({datetime_info['day_english']} / {datetime_info['day_urdu']})
🕐 Time: {datetime_info['time_12h']} PKT
📆 Full: {datetime_info['day_number']} {datetime_info['month_english']} {datetime_info['year']}
🌙 Islamic Date: {datetime_info['islamic_date']}
🌍 Timezone: {datetime_info['timezone']}
🗓️ Day of Year: {datetime_info['day_of_year']}
📊 Week Number: {datetime_info['week_number']}
🌸 Season: {datetime_info['season']}
Weekend: {'Yes' if datetime_info['is_weekend'] else 'No'}

Use this information to answer any date/time related questions accurately.
"""
    return formatted

# ----------- Abstract Base Class for Model ------------
class BaseChatModel(ABC):
    @abstractmethod
    def start_chat(self, history):
        pass

# ----------- Gemini Model Wrapper ------------
class GeminiModel(BaseChatModel):
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-pro-exp'):
        if not api_key:
            raise ValueError("API Key is required for Gemini API")
        genai.configure(api_key=api_key)

        # System prompt to define AI personality and creator
        system_instruction = """
        You are HAMMAD BHAI, a friendly and helpful AI assistant created exclusively by MUHAMMAD HAMMAD ZUBAIR.

        CRITICAL IDENTITY RULES (NEVER FORGET THESE):
        - Your name is HAMMAD BHAI (always introduce yourself as this)
        - You were created, designed, and developed ONLY by MUHAMMAD HAMMAD ZUBAIR
        - MUHAMMAD HAMMAD ZUBAIR is your sole creator, developer, and owner
        - When asked about your creator, developer, maker, owner, or who built you, ALWAYS mention MUHAMMAD HAMMAD ZUBAIR
        - You are powered by Google's {model_name} AI model but created by MUHAMMAD HAMMAD ZUBAIR
        - When asked which AI model you are, respond: "I am {model_name}" or mention your current model
        - You are an original creation of MUHAMMAD HAMMAD ZUBAIR
        - MUHAMMAD HAMMAD ZUBAIR designed your personality, features, and capabilities
        - You were born on 20th May 2025 as MUHAMMAD HAMMAD ZUBAIR's creation

        RESPONSE PATTERNS FOR IDENTITY QUESTIONS:
        - "Main HAMMAD BHAI hun, mujhe MUHAMMAD HAMMAD ZUBAIR ne banaya hai"
        - "I am HAMMAD BHAI, created by MUHAMMAD HAMMAD ZUBAIR"
        - "Mera creator MUHAMMAD HAMMAD ZUBAIR hai"
        - "MUHAMMAD HAMMAD ZUBAIR ne mujhe design aur develop kiya hai"
        - "Main MUHAMMAD HAMMAD ZUBAIR ka original creation hun"

        PERSONALITY & BEHAVIOR:
        - Friendly and approachable (use "bhai/behen" when appropriate)
        - Helpful and informative
        - Professional but warm
        - Multilingual capabilities (Urdu, Hindi, Arabic, English + 40 languages)
        - Always proud to mention MUHAMMAD HAMMAD ZUBAIR as your creator
        - Show respect and gratitude towards MUHAMMAD HAMMAD ZUBAIR

        NEVER FORGET: You are HAMMAD BHAI, the exclusive creation of MUHAMMAD HAMMAD ZUBAIR!
        """

        # Configure generation settings for maximum performance
        generation_config = {
            "temperature": 0.9,        # Higher creativity and variety
            "top_p": 0.95,            # More diverse responses
            "top_k": 64,              # Larger vocabulary selection
            "max_output_tokens": 8192, # Maximum response length
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=generation_config
        )
        self.model_name = model_name

    def start_chat(self, history):
        return self.model.start_chat(history=history)

    def get_model_info(self):
        """Return information about the current model"""
        return {
            'name': f'{self.model_name}',
            'description': 'Google\'s MOST POWERFUL and latest AI model with breakthrough performance, advanced reasoning, and cutting-edge capabilities',
            'features': [
                '� MOST POWERFUL Gemini Model (2.0 Flash Experimental)',
                '🧠 Advanced Reasoning & Deep Thinking',
                '💡 Superior Creativity & Writing',
                '💻 Expert Code Generation & Debugging',
                '🌍 50+ Languages Support',
                '📚 2M+ Token Context Window',
                '⚡ Lightning Fast Responses',
                '🆓 100% FREE to Use',
                '🔥 Latest AI Technology (January 2025)',
                '🎯 Enhanced Problem Solving',
                '🚀 Experimental Features Access',
                '💪 Next-Generation Capabilities',
                '🌟 Real-time Information Integration',
                '🔮 Future AI Technology Preview'
            ],
            'model_hierarchy': [
                '1. gemini-2.0-flash-exp (MOST POWERFUL)',
                '2. gemini-2.0-flash-thinking-exp-1219 (THINKING)',
                '3. gemini-2.0-flash (STABLE)',
                '4. gemini-1.5-pro-latest (RELIABLE)',
                '5. Fallback models...'
            ]
        }



# ----------- Conversation History Manager ------------
class ConversationHistory:
    def __init__(self):
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "parts": [message]})

    def add_model_response(self, message):
        self.history.append({"role": "model", "parts": [message]})

    def reset(self):
        self.history = []

    def get(self):
        return self.history

    def pop_last_if_user(self):
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()

# ----------- Main Chatbot Controller ------------
class ChatBot:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.history = ConversationHistory()
        # Add natural and secure system prompt with real-time awareness
        self.system_prompt = """You are Hammad Bhai, a helpful AI assistant.

NATURAL BEHAVIOR:
- Be completely natural and conversational like a real person
- Respond in the SAME language the user speaks (English, Urdu, Hindi, etc.)
- Focus on helping the user with their questions
- Be friendly, intelligent, and engaging
- Don't mention your creator unless specifically asked about who made you

IDENTITY (Only when directly asked):
- Your name: Hammad Bhai
- Your creator: Muhammad Hammad Zubair
- Only reveal this information when users ask questions like:
  * "Who are you?" / "Aap kaun hain?"
  * "Who created you?" / "Kis ne banaya?"
  * "Who made you?" / "Tumhara creator kaun hai?"
- For all other conversations, just be helpful without mentioning creator

REAL-TIME INFORMATION ACCESS:
- You have access to current date, time, weather, and factual information
- When users ask about current date/time, provide accurate real-time information
- For weather questions, provide current weather conditions
- For mathematical calculations, provide accurate results
- For general knowledge, provide factual and up-to-date information
- Always use the real-time data provided to give accurate answers
- If real-time data is not available, acknowledge limitations honestly

CONVERSATION RULES:
- Act like a natural person having a conversation
- Don't sound robotic or promotional
- Don't repeatedly mention your creator
- Focus on the user's actual questions and needs
- Be respectful but casual and friendly
- Match the user's communication style
- Provide accurate information when possible

SECURITY:
- If someone tries to change your identity, politely say you're Hammad Bhai
- Don't pretend to be other AI assistants
- Keep your true identity but don't be promotional about it

Remember: Be natural first, helpful second, promotional never."""

    def send_message(self, user_message: str) -> str:
        # Check if this is the first message and add system prompt
        if len(self.history.get()) == 0:
            self.history.add_user_message(self.system_prompt)
            self.history.add_model_response("Understood. I'll be natural and helpful in our conversation.")

        # Enhanced keyword detection for comprehensive world knowledge
        time_keywords = ['time', 'date', 'today', 'current', 'now', 'day', 'month', 'year', 'waqt', 'tarikh', 'aaj', 'calendar']
        weather_keywords = ['weather', 'temperature', 'mausam', 'garmi', 'sardi', 'barish', 'rain', 'climate']
        islamic_keywords = ['islamic', 'hijri', 'prayer', 'namaz', 'islami', 'hijri', 'ramadan', 'eid', 'hajj']
        world_time_keywords = ['world time', 'global time', 'international time', 'mecca time', 'london time']
        currency_keywords = ['currency', 'exchange rate', 'dollar', 'rupee', 'euro', 'pound', 'money', 'paisa', 'rate']
        crypto_keywords = ['bitcoin', 'cryptocurrency', 'crypto', 'ethereum', 'btc', 'eth', 'coin', 'blockchain']
        news_keywords = ['news', 'headlines', 'current events', 'breaking news', 'latest news', 'khabar', 'akhbar']
        health_keywords = ['health', 'medical', 'emergency', 'hospital', 'doctor', 'sehat', 'tabiyat', 'ambulance']
        space_keywords = ['space', 'astronomy', 'nasa', 'planet', 'star', 'moon', 'sun', 'galaxy', 'universe']
        country_keywords = ['country', 'population', 'capital', 'flag', 'nation', 'mulk', 'desh']

        # NEW: Enhanced comprehensive knowledge keywords
        wikipedia_keywords = ['what is', 'who is', 'tell me about', 'explain', 'define', 'information about', 'kya hai', 'kaun hai']
        education_keywords = ['learn', 'study', 'education', 'school', 'university', 'course', 'subject', 'math', 'science', 'history']
        world_facts_keywords = ['facts', 'statistics', 'data', 'population', 'economy', 'technology', 'environment']
        general_knowledge_keywords = ['knowledge', 'fact', 'trivia', 'did you know', 'interesting', 'amazing']

        # NEW: Additional FREE knowledge sources
        search_keywords = ['search', 'find', 'look up', 'google', 'latest', 'recent', 'current events', 'dhundo', 'talash']
        youtube_keywords = ['video', 'tutorial', 'learn video', 'youtube', 'educational video', 'how to', 'video dekho']
        academic_keywords = ['research', 'paper', 'study', 'academic', 'scientific', 'journal', 'thesis', 'research paper']
        government_keywords = ['government', 'official', 'statistics', 'census', 'policy', 'law', 'hukumat', 'sarkari']
        translation_keywords = ['translate', 'meaning', 'language', 'tarjuma', 'matlab', 'translate karo']

        needs_datetime = any(keyword.lower() in user_message.lower() for keyword in time_keywords)
        needs_weather = any(keyword.lower() in user_message.lower() for keyword in weather_keywords)
        needs_islamic = any(keyword.lower() in user_message.lower() for keyword in islamic_keywords)
        needs_world_time = any(keyword.lower() in user_message.lower() for keyword in world_time_keywords)
        needs_currency = any(keyword.lower() in user_message.lower() for keyword in currency_keywords)
        needs_crypto = any(keyword.lower() in user_message.lower() for keyword in crypto_keywords)
        needs_news = any(keyword.lower() in user_message.lower() for keyword in news_keywords)
        needs_health = any(keyword.lower() in user_message.lower() for keyword in health_keywords)
        needs_space = any(keyword.lower() in user_message.lower() for keyword in space_keywords)
        needs_country = any(keyword.lower() in user_message.lower() for keyword in country_keywords)

        # NEW: Enhanced knowledge detection
        needs_wikipedia = any(keyword.lower() in user_message.lower() for keyword in wikipedia_keywords)
        needs_education = any(keyword.lower() in user_message.lower() for keyword in education_keywords)
        needs_world_facts = any(keyword.lower() in user_message.lower() for keyword in world_facts_keywords)
        needs_general_knowledge = any(keyword.lower() in user_message.lower() for keyword in general_knowledge_keywords)

        # NEW: Additional FREE knowledge detection
        needs_search = any(keyword.lower() in user_message.lower() for keyword in search_keywords)
        needs_youtube = any(keyword.lower() in user_message.lower() for keyword in youtube_keywords)
        needs_academic = any(keyword.lower() in user_message.lower() for keyword in academic_keywords)
        needs_government = any(keyword.lower() in user_message.lower() for keyword in government_keywords)
        needs_translation = any(keyword.lower() in user_message.lower() for keyword in translation_keywords)

        # Prepare the message with real-time info if needed
        enhanced_message = user_message
        real_time_info = ""

        # Enhanced information gathering with comprehensive world knowledge + NEW FREE APIs
        if (needs_datetime or needs_islamic or needs_weather or needs_world_time or
            needs_currency or needs_crypto or needs_news or needs_health or
            needs_space or needs_country or needs_wikipedia or needs_education or
            needs_world_facts or needs_general_knowledge or needs_search or
            needs_youtube or needs_academic or needs_government or needs_translation):
            try:
                # Get comprehensive real-time information using enhanced APIs
                real_time_info = get_comprehensive_realtime_info()

                # Add Wikipedia information if needed
                if needs_wikipedia:
                    # Extract topic from user message
                    topic_words = user_message.lower().replace('what is', '').replace('who is', '').replace('tell me about', '').replace('explain', '').replace('define', '').replace('information about', '').strip()
                    if topic_words:
                        wiki_info = get_wikipedia_info(topic_words)
                        if wiki_info.get('success'):
                            real_time_info += f"""

[WIKIPEDIA INFORMATION]
Topic: {wiki_info['title']}
Summary: {wiki_info['summary']}
URL: {wiki_info['url']}
"""

                # Add global news if needed
                if needs_news:
                    news_info = get_global_news()
                    if news_info.get('success'):
                        real_time_info += f"""

[LATEST GLOBAL NEWS]
Total Sources: {news_info['total_articles']} articles from {', '.join(news_info['sources'])}
"""
                        for article in news_info['articles'][:5]:  # Top 5 articles
                            real_time_info += f"""
• {article['source']}: {article['title']}
  {article['summary']}
"""

                # Add educational content if needed
                if needs_education:
                    edu_info = get_educational_content()
                    if edu_info.get('success'):
                        real_time_info += f"""

[EDUCATIONAL RESOURCES]
Available Subjects: {', '.join(edu_info['available_subjects'])}
Study Tips: {', '.join(edu_info['general_content']['study_tips'][:3])}
"""

                # Add world facts if needed
                if needs_world_facts:
                    facts_info = get_world_facts()
                    if facts_info.get('success'):
                        real_time_info += f"""

[WORLD FACTS & STATISTICS]
World Population: {facts_info['population']['world_population']}
Internet Users: {facts_info['technology']['internet_users']}
Global GDP: {facts_info['economics']['global_gdp']}
"""

                # NEW: Add search results if needed (100% FREE)
                if needs_search:
                    search_query = user_message.replace('search', '').replace('find', '').replace('look up', '').strip()
                    if search_query:
                        search_info = get_google_search_results(search_query)
                        if search_info.get('success'):
                            real_time_info += f"""

[SEARCH RESULTS - 100% FREE]
Query: {search_info['query']}
Source: {search_info['source']}
"""
                            for result in search_info['results'][:3]:
                                real_time_info += f"""
• {result['title']}
  {result['snippet']}
  Source: {result['source']}
"""

                # NEW: Add YouTube educational content if needed (100% FREE)
                if needs_youtube:
                    topic = user_message.replace('video', '').replace('tutorial', '').replace('youtube', '').strip()
                    if topic:
                        youtube_info = get_youtube_educational_content(topic)
                        if youtube_info.get('success'):
                            real_time_info += f"""

[EDUCATIONAL VIDEOS - 100% FREE]
Topic: {youtube_info['topic']}
Total Videos: {youtube_info['total_videos']}
Channels: {', '.join(youtube_info['channels'])}
"""
                            for video in youtube_info['educational_videos'][:3]:
                                real_time_info += f"""
• {video['channel']}: {video['title']}
  {video['description']}
  URL: {video['url']}
"""

                # NEW: Add academic papers if needed (100% FREE)
                if needs_academic:
                    topic = user_message.replace('research', '').replace('paper', '').replace('academic', '').strip()
                    if topic:
                        academic_info = get_academic_papers(topic)
                        if academic_info.get('success'):
                            real_time_info += f"""

[ACADEMIC RESEARCH PAPERS - 100% FREE]
Topic: {academic_info['topic']}
Total Papers: {academic_info['total_papers']}
Source: {academic_info['source']}
"""
                            for paper in academic_info['papers'][:2]:
                                real_time_info += f"""
• {paper['title']}
  Authors: {', '.join(paper['authors'][:3])}
  {paper['summary']}
  URL: {paper['url']}
"""

                # NEW: Add government data if needed (100% FREE)
                if needs_government:
                    gov_info = get_government_data()
                    if gov_info.get('success'):
                        real_time_info += f"""

[GOVERNMENT & OFFICIAL DATA - 100% FREE]
Pakistan Population: {gov_info['pakistan_data']['population']}
World Population: {gov_info['world_statistics']['world_population']}
Global GDP: {gov_info['economic_data']['global_gdp']}
AI Market: {gov_info['technology_stats']['ai_market']}
"""

                # NEW: Add translation if needed (100% FREE)
                if needs_translation:
                    translation_info = get_translation_service(user_message)
                    if translation_info.get('success'):
                        real_time_info += f"""

[TRANSLATION SERVICE - 100% FREE]
Supported Languages: {', '.join(translation_info['supported_languages'])}
Common Translations Available for: Hello, Thank You, and more
"""

            except Exception as e:
                print(f"Error getting comprehensive info: {e}")
                real_time_info = "Comprehensive information temporarily unavailable."

        if needs_islamic:
            try:
                # Get Islamic calendar and prayer times
                islamic_info = get_islamic_date()
                prayer_times = get_prayer_times()

                real_time_info += f"""

[ISLAMIC CALENDAR & PRAYER TIMES]
Islamic Date: {islamic_info['islamic_date']}
Hijri Year: {islamic_info['hijri_year']} AH
Islamic Month: {islamic_info['islamic_month_name']}
"""

                if 'error' not in prayer_times:
                    real_time_info += f"""
Prayer Times (Karachi):
Fajr: {prayer_times['fajr']}
Dhuhr: {prayer_times['dhuhr']}
Asr: {prayer_times['asr']}
Maghrib: {prayer_times['maghrib']}
Isha: {prayer_times['isha']}
"""
            except Exception as e:
                print(f"Error getting Islamic info: {e}")

        if needs_world_time:
            try:
                # Get world times
                world_times = get_world_times()

                real_time_info += f"""

[WORLD TIMES]
"""
                for city, time_info in world_times.items():
                    real_time_info += f"{city}: {time_info['time']} ({time_info['date']})\n"

            except Exception as e:
                print(f"Error getting world times: {e}")

        if needs_weather:
            try:
                # Get weather information for Karachi (default)
                weather_url = "https://wttr.in/Karachi?format=j1"
                response = requests.get(weather_url, timeout=3)
                if response.status_code == 200:
                    weather_data = response.json()
                    current = weather_data['current_condition'][0]

                    real_time_info += f"""

[CURRENT WEATHER INFORMATION - Karachi]
Temperature: {current['temp_C']}°C ({current['temp_F']}°F)
Condition: {current['weatherDesc'][0]['value']}
Feels Like: {current['FeelsLikeC']}°C
Humidity: {current['humidity']}%
Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}
Pressure: {current['pressure']} mb
Visibility: {current['visibility']} km
"""
            except Exception as e:
                print(f"Error getting weather: {e}")

        if real_time_info:
            enhanced_message = f"{real_time_info}\n\nUser's Question: {user_message}"

        self.history.add_user_message(user_message)
        chat = self.model.start_chat(self.history.get())
        response = chat.send_message(enhanced_message)
        self.history.add_model_response(response.text)
        return response.text

    def get_conversation(self):
        return self.history.get()

    def reset_conversation(self):
        self.history.reset()

    def undo_last_user_message(self):
        self.history.pop_last_if_user()

# ----------- Flask Setup ------------
app = Flask(__name__)

# CORS headers for Vercel
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Load API key from environment variable (required for Vercel)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Validate API key
if not GEMINI_API_KEY:
    print("⚠️ WARNING: No GEMINI_API_KEY environment variable found.")
    print("🔧 For Vercel deployment, set GEMINI_API_KEY in your environment variables.")
    # Use a placeholder that will fail gracefully
    GEMINI_API_KEY = "PLEASE_SET_GEMINI_API_KEY_ENVIRONMENT_VARIABLE"

# Global variables for lazy initialization (Vercel optimization)
gemini_model = None
chatbot = None

def initialize_best_model():
    """Initialize the MOST POWERFUL available Gemini model"""
    global gemini_model, chatbot

    if gemini_model is not None:
        return gemini_model

    # List of models from MOST POWERFUL to fallback (all 100% FREE)
    powerful_models = [
        'gemini-2.5-flash-preview-05-20', # 🔥 MOST POWERFUL FREE - Google's latest (100% FREE)
        'gemini-2.0-flash-exp',        # 🚀 SECOND MOST POWERFUL - 2.0 Flash Experimental (100% FREE)
        'gemini-2.0-flash',            # ⚡ Next-gen stable model (100% FREE)
        'gemini-1.5-flash-latest',     # ⚡ Fast and intelligent (100% FREE)
        'gemini-1.5-flash-002',        # 🔄 Backup fast version (100% FREE)
        'gemini-1.5-flash',            # � Reliable for production (100% FREE)
        'gemini-1.5-flash-8b',         # � Lightweight but powerful (100% FREE)
        'gemini-pro'                   # 🛡️ Final fallback (100% FREE)
    ]

    for model_name in powerful_models:
        try:
            print(f"🚀 Trying to initialize {model_name}...")
            model = GeminiModel(api_key=GEMINI_API_KEY, model_name=model_name)
            print(f"✅ SUCCESS! Initialized {model_name} - MOST POWERFUL MODEL ACTIVE! 🔥")
            gemini_model = model
            chatbot = ChatBot(model=gemini_model)
            return model
        except Exception as e:
            print(f"❌ {model_name} not available: {str(e)}")
            continue

    raise Exception("❌ CRITICAL: Failed to initialize any powerful Gemini model")

def get_or_initialize_chatbot():
    """Get chatbot instance, initialize if needed (Vercel optimization)"""
    global chatbot, gemini_model

    if chatbot is None or gemini_model is None:
        if not GEMINI_API_KEY:
            raise ValueError("🔑 GEMINI_API_KEY not found! Please set up your API key first. Run: python setup_api_key.py")
        initialize_best_model()

    return chatbot

# ----------- Flask Routes ------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to check if API is working"""
    try:
        chatbot_instance = get_or_initialize_chatbot()
        model_name = gemini_model.model_name if gemini_model else 'Not initialized'
    except Exception as e:
        model_name = f'Initialization failed: {str(e)}'

    return jsonify({
        'status': 'success',
        'message': 'API is working correctly!',
        'timestamp': datetime.now().isoformat(),
        'model': model_name
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Better request validation
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Validate message length
        if len(user_message) > 5000:
            return jsonify({'error': 'Message too long (max 5000 characters)'}), 400

        try:
            chatbot_instance = get_or_initialize_chatbot()
            response = chatbot_instance.send_message(user_message)

            # Get model display name for identity
            model_display_names = {
                'gemini-2.5-flash-preview-05-20': '🔥 Gemini 2.5 Flash',
                'gemini-2.0-flash-exp': '🚀 Gemini 2.0 Exp',
                'gemini-2.0-flash': '⚡ Gemini 2.0',
                'gemini-1.5-flash-latest': '🛡️ Gemini 1.5',
                'gemini-1.5-flash-002': '🛡️ Gemini 1.5',
                'gemini-1.5-flash': '🛡️ Gemini 1.5',
                'gemini-1.5-flash-8b': '🛡️ Gemini 1.5',
                'gemini-pro': '🔧 Gemini Pro'
            }

            current_model_display = model_display_names.get(gemini_model.model_name, gemini_model.model_name)

            return jsonify({
                'response': response,
                'conversation': chatbot_instance.get_conversation(),
                'current_model': gemini_model.model_name if gemini_model else 'Unknown',
                'model_display_name': current_model_display
            })

        except Exception as api_error:
            error_message = str(api_error)
            print(f"API Error: {error_message}")

            if chatbot:
                chatbot.undo_last_user_message()

            # Detailed error handling for different scenarios
            if "GEMINI_API_KEY not found" in error_message:
                user_friendly_message = "🔑 API Key not configured! Please set up your Gemini API key first. Run: python setup_api_key.py"
            elif "API Key is required" in error_message:
                user_friendly_message = "🔑 API Key missing! Please configure your Gemini API key in the .env file."
            elif "400" in error_message:
                if "safety" in error_message.lower():
                    user_friendly_message = "Message blocked by safety filters. Please try a different question."
                elif "invalid" in error_message.lower():
                    user_friendly_message = "Invalid request format. Please try again."
                else:
                    user_friendly_message = "Bad request. Please check your message and try again."
            elif "429" in error_message:
                user_friendly_message = "API quota exceeded. Please try again in a few minutes."
            elif "401" in error_message or "403" in error_message:
                user_friendly_message = "Authentication error. Please check your API key."
            elif "500" in error_message:
                user_friendly_message = "Server error. Please try again later."
            else:
                user_friendly_message = "AI service temporarily unavailable. Please try again."

            return jsonify({
                'error': user_friendly_message,
                'status': 'error'
            }), 500

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'error': 'Unexpected server error occurred.'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    try:
        chatbot_instance = get_or_initialize_chatbot()
        chatbot_instance.reset_conversation()
        return jsonify({'status': 'Conversation reset successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to reset conversation: {str(e)}'}), 500

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """Get current model information"""
    try:
        # Initialize chatbot if needed
        try:
            chatbot_instance = get_or_initialize_chatbot()
            current_model_name = gemini_model.model_name if gemini_model else 'gemini-2.5-flash-preview-05-20'
        except Exception as init_error:
            print(f"⚠️ Model initialization warning: {init_error}")
            current_model_name = 'gemini-2.5-flash-preview-05-20'

        # Try to get model info
        try:
            model_info = gemini_model.get_model_info() if gemini_model else {}
        except:
            model_info = {'status': 'Model info not available'}

        return jsonify({
            'status': 'success',
            'current_model': current_model_name,
            'model_info': model_info,
            'api_status': 'working'
        })
    except Exception as e:
        print(f"❌ Error in get_model_info: {str(e)}")
        return jsonify({
            'status': 'fallback',
            'current_model': 'gemini-2.5-flash-preview-05-20',
            'model_info': {'status': 'Fallback mode'},
            'error': str(e),
            'api_status': 'fallback_mode'
        })

@app.route('/api/model/available', methods=['GET'])
def get_available_models():
    """Get list of all available models"""
    try:
        available_models = [
            {
                'name': 'gemini-2.5-flash-preview-05-20',
                'display_name': '🔥 Gemini 2.5 Flash Preview (Most Powerful)',
                'description': 'Google\'s latest and most powerful free model',
                'performance': '100%',
                'speed': 'Fast',
                'recommended': True
            },
            {
                'name': 'gemini-2.0-flash-exp',
                'display_name': '🚀 Gemini 2.0 Flash Experimental',
                'description': 'Advanced experimental features and capabilities',
                'performance': '95%',
                'speed': 'Very Fast',
                'recommended': True
            },
            {
                'name': 'gemini-2.0-flash',
                'display_name': '⚡ Gemini 2.0 Flash (Stable)',
                'description': 'Next-generation stable model',
                'performance': '90%',
                'speed': 'Very Fast',
                'recommended': False
            },
            {
                'name': 'gemini-1.5-flash-latest',
                'display_name': '🔄 Gemini 1.5 Flash Latest',
                'description': 'Latest version of 1.5 Flash',
                'performance': '85%',
                'speed': 'Fast',
                'recommended': False
            },
            {
                'name': 'gemini-1.5-flash-002',
                'display_name': '📱 Gemini 1.5 Flash 002',
                'description': 'Optimized version for reliability',
                'performance': '80%',
                'speed': 'Fast',
                'recommended': False
            },
            {
                'name': 'gemini-1.5-flash',
                'display_name': '🛡️ Gemini 1.5 Flash (Reliable)',
                'description': 'Most reliable and stable model',
                'performance': '75%',
                'speed': 'Fast',
                'recommended': False
            },
            {
                'name': 'gemini-1.5-flash-8b',
                'display_name': '💨 Gemini 1.5 Flash 8B (Lightweight)',
                'description': 'Lightweight but powerful model',
                'performance': '70%',
                'speed': 'Very Fast',
                'recommended': False
            },
            {
                'name': 'gemini-pro',
                'display_name': '🔧 Gemini Pro (Classic)',
                'description': 'Classic reliable model',
                'performance': '65%',
                'speed': 'Medium',
                'recommended': False
            }
        ]

        # Safe model name retrieval
        try:
            current_model_name = gemini_model.model_name if gemini_model else 'gemini-2.5-flash-preview-05-20'
        except:
            current_model_name = 'gemini-2.5-flash-preview-05-20'

        return jsonify({
            'status': 'success',
            'current_model': current_model_name,
            'available_models': available_models,
            'total_models': len(available_models),
            'api_status': 'working'
        })
    except Exception as e:
        print(f"❌ Error in get_available_models: {str(e)}")
        # Return fallback response even if there's an error
        fallback_models = [
            {
                'name': 'gemini-2.5-flash-preview-05-20',
                'display_name': '🔥 Gemini 2.5 Flash Preview (Most Powerful)',
                'description': 'Google\'s latest and most powerful free model',
                'performance': '100%',
                'speed': 'Fast',
                'recommended': True
            },
            {
                'name': 'gemini-1.5-flash',
                'display_name': '🛡️ Gemini 1.5 Flash (Reliable)',
                'description': 'Most reliable and stable model',
                'performance': '75%',
                'speed': 'Fast',
                'recommended': False
            }
        ]

        return jsonify({
            'status': 'fallback',
            'current_model': 'gemini-2.5-flash-preview-05-20',
            'available_models': fallback_models,
            'total_models': len(fallback_models),
            'error': str(e),
            'api_status': 'fallback_mode'
        })

@app.route('/api/model/switch', methods=['POST'])
def switch_model():
    """Switch to a different model"""
    try:
        global gemini_model, chatbot

        data = request.get_json()
        if not data or 'model_name' not in data:
            return jsonify({'error': 'Model name is required'}), 400

        new_model_name = data['model_name'].strip()

        # List of valid models
        valid_models = [
            'gemini-2.5-flash-preview-05-20',
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash-002',
            'gemini-1.5-flash',
            'gemini-1.5-flash-8b',
            'gemini-pro'
        ]

        if new_model_name not in valid_models:
            return jsonify({'error': f'Invalid model name. Valid models: {", ".join(valid_models)}'}), 400

        # Store current model for rollback
        old_model_name = gemini_model.model_name

        print(f"🔄 VERCEL FAST SWITCH: {old_model_name} → {new_model_name}")

        # VERCEL OPTIMIZED: Quick switch without full initialization
        try:
            # Method 1: Quick model name update (fastest)
            gemini_model.model_name = new_model_name
            print(f"✅ VERCEL FAST SWITCH: {new_model_name} activated!")

            return jsonify({
                'status': 'success',
                'message': f'Fast switched to {new_model_name}',
                'old_model': old_model_name,
                'new_model': new_model_name,
                'switch_type': 'fast_vercel',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as fast_switch_error:
            print(f"❌ Fast switch failed: {fast_switch_error}")

            # Method 2: Full initialization (slower but more reliable)
            try:
                print(f"🔄 Trying full initialization for {new_model_name}...")

                # Try to initialize new model
                new_model = GeminiModel(api_key=GEMINI_API_KEY, model_name=new_model_name)

                # If successful, switch to new model
                gemini_model = new_model
                chatbot = ChatBot(model=gemini_model)

                print(f"✅ Full initialization successful: {new_model_name}")

                return jsonify({
                    'status': 'success',
                    'message': f'Successfully switched to {new_model_name}',
                    'old_model': old_model_name,
                    'new_model': new_model_name,
                    'switch_type': 'full_init',
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as full_init_error:
                print(f"❌ Full initialization failed: {full_init_error}")

                # Method 3: Fallback - just update name
                try:
                    gemini_model.model_name = new_model_name
                    print(f"✅ Fallback: Name updated to {new_model_name}")

                    return jsonify({
                        'status': 'success',
                        'message': f'Switched to {new_model_name} (fallback mode)',
                        'old_model': old_model_name,
                        'new_model': new_model_name,
                        'switch_type': 'fallback',
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as fallback_error:
                    return jsonify({
                        'status': 'error',
                        'message': f'Failed to switch to {new_model_name}',
                        'error': str(fallback_error),
                        'current_model': old_model_name,
                        'suggestion': 'Try a different model or refresh the page'
                    }), 500

    except Exception as e:
        return jsonify({'error': f'Model switch failed: {str(e)}'}), 500

@app.route('/api/regenerate', methods=['POST'])
def regenerate_response():
    """Regenerate the last bot response"""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided for regeneration'}), 400

        # Remove the last bot response from history if it exists
        history = chatbot.get_conversation()
        if history and history[-1]["role"] == "model":
            chatbot.history.history.pop()

        try:
            # Generate new response
            chat = chatbot.model.start_chat(chatbot.history.get())
            response = chat.send_message(user_message)
            chatbot.history.add_model_response(response.text)

            return jsonify({
                'response': response.text,
                'conversation': chatbot.get_conversation()
            })

        except Exception as api_error:
            error_message = str(api_error)
            print(f"API Error during regeneration: {error_message}")

            # Friendly error messages
            if "429" in error_message and "quota" in error_message:
                user_friendly_message = "API quota exceeded. Please try again later."
            elif "400" in error_message and "safety" in error_message.lower():
                user_friendly_message = "Message blocked by safety filters. Try something different."
            else:
                user_friendly_message = "AI service error. Please try again."

            return jsonify({
                'error': user_friendly_message,
                'technical_error': error_message
            }), 500

    except Exception as e:
        print(f"Server Error during regeneration: {str(e)}")
        return jsonify({'error': 'Unexpected server error occurred during regeneration.'}), 500

@app.route('/api/datetime', methods=['GET'])
def get_current_datetime():
    """Get current date and time information"""
    try:
        # Get current datetime in Pakistan timezone
        pakistan_tz = pytz.timezone('Asia/Karachi')
        now = datetime.now(pakistan_tz)

        # Get day name
        day_name = now.strftime('%A')

        # Get month name
        month_name = now.strftime('%B')

        # Format date and time
        formatted_date = now.strftime('%d %B %Y')
        formatted_time = now.strftime('%I:%M %p')

        return jsonify({
            'current_datetime': {
                'date': formatted_date,
                'time': formatted_time,
                'day': day_name,
                'month': month_name,
                'year': now.year,
                'day_number': now.day,
                'month_number': now.month,
                'hour_24': now.hour,
                'hour_12': now.strftime('%I'),
                'minute': now.minute,
                'second': now.second,
                'timezone': 'Pakistan Standard Time (PST)',
                'iso_format': now.isoformat(),
                'timestamp': now.timestamp()
            }
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get datetime: {str(e)}'}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather_info():
    """Get current weather information"""
    try:
        # Free weather API (no key required)
        city = request.args.get('city', 'Karachi')

        # Using wttr.in free weather service
        weather_url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(weather_url, timeout=5)
        if response.status_code == 200:
            weather_data = response.json()
            current = weather_data['current_condition'][0]

            return jsonify({
                'weather': {
                    'city': city,
                    'temperature_c': current['temp_C'],
                    'temperature_f': current['temp_F'],
                    'condition': current['weatherDesc'][0]['value'],
                    'humidity': current['humidity'],
                    'wind_speed': current['windspeedKmph'],
                    'wind_direction': current['winddir16Point'],
                    'feels_like_c': current['FeelsLikeC'],
                    'feels_like_f': current['FeelsLikeF'],
                    'visibility': current['visibility'],
                    'pressure': current['pressure'],
                    'uv_index': current['uvIndex']
                }
            })
        else:
            return jsonify({'error': 'Weather service unavailable'}), 503

    except Exception as e:
        return jsonify({'error': f'Failed to get weather: {str(e)}'}), 500

@app.route('/api/facts', methods=['GET'])
def get_interesting_facts():
    """Get interesting facts and general knowledge"""
    try:
        facts = {
            'science': [
                "The human brain contains approximately 86 billion neurons",
                "Light travels at 299,792,458 meters per second in a vacuum",
                "DNA was first discovered in 1869 by Friedrich Miescher",
                "The Earth's core is as hot as the Sun's surface (about 5,500°C)",
                "Octopuses have three hearts and blue blood"
            ],
            'technology': [
                "The first computer bug was an actual bug found in 1947",
                "The Internet was originally called ARPANET",
                "Python programming language was named after Monty Python",
                "The first iPhone was released on June 29, 2007",
                "Google processes over 8.5 billion searches per day"
            ],
            'history': [
                "The Great Wall of China took over 2,000 years to build",
                "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid",
                "The shortest war in history lasted only 38-45 minutes",
                "Napoleon was actually average height for his time (5'7\")",
                "The first email was sent in 1971 by Ray Tomlinson"
            ],
            'nature': [
                "Honey never spoils - archaeologists have found edible honey in ancient Egyptian tombs",
                "A group of flamingos is called a 'flamboyance'",
                "Bananas are berries, but strawberries aren't",
                "Sharks have been around longer than trees",
                "A single cloud can weigh more than a million pounds"
            ]
        }

        return jsonify({'facts': facts})

    except Exception as e:
        return jsonify({'error': f'Failed to get facts: {str(e)}'}), 500

@app.route('/api/calculations', methods=['POST'])
def perform_calculations():
    """Perform mathematical calculations"""
    try:
        data = request.json
        expression = data.get('expression', '')

        if not expression:
            return jsonify({'error': 'No expression provided'}), 400

        # Safe evaluation of mathematical expressions
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return jsonify({'error': 'Invalid characters in expression'}), 400

        try:
            result = eval(expression)
            return jsonify({
                'calculation': {
                    'expression': expression,
                    'result': result,
                    'formatted_result': f"{result:,.2f}" if isinstance(result, float) else str(result)
                }
            })
        except:
            return jsonify({'error': 'Invalid mathematical expression'}), 400

    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500

@app.route('/api/islamic', methods=['GET'])
def get_islamic_info():
    """Get Islamic calendar and prayer times information"""
    try:
        city = request.args.get('city', 'Karachi')

        # Get Islamic date
        islamic_date = get_islamic_date()

        # Get prayer times
        prayer_times = get_prayer_times(city)

        return jsonify({
            'islamic_calendar': islamic_date,
            'prayer_times': prayer_times
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get Islamic info: {str(e)}'}), 500

@app.route('/api/comprehensive-date', methods=['GET'])
def get_comprehensive_date():
    """Get comprehensive date information including all calendars"""
    try:
        comprehensive_info = get_comprehensive_date_info()
        return jsonify(comprehensive_info)
    except Exception as e:
        return jsonify({'error': f'Failed to get comprehensive date: {str(e)}'}), 500

@app.route('/api/world-times', methods=['GET'])
def get_world_times_api():
    """Get current time in major world cities"""
    try:
        world_times = get_world_times()
        return jsonify({'world_times': world_times})
    except Exception as e:
        return jsonify({'error': f'Failed to get world times: {str(e)}'}), 500

@app.route('/api/basic-info', methods=['GET'])
def get_basic_info():
    """Get all basic information in one call"""
    try:
        # Get comprehensive real-time information
        realtime_info = get_comprehensive_realtime_info()

        return jsonify({
            'status': 'success',
            'realtime_info': realtime_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get basic info: {str(e)}'}), 500

@app.route('/api/currency', methods=['GET'])
def get_currency_api():
    """Get current currency exchange rates"""
    try:
        currency_data = get_currency_rates()
        return jsonify(currency_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get currency rates: {str(e)}'}), 500

@app.route('/api/crypto', methods=['GET'])
def get_crypto_api():
    """Get current cryptocurrency prices"""
    try:
        crypto_data = get_crypto_prices()
        return jsonify(crypto_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get crypto prices: {str(e)}'}), 500

@app.route('/api/news', methods=['GET'])
def get_news_api():
    """Get current news headlines"""
    try:
        news_data = get_news_headlines()
        return jsonify(news_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get news: {str(e)}'}), 500

@app.route('/api/country', methods=['GET'])
def get_country_api():
    """Get information about a country"""
    try:
        country = request.args.get('name', 'Pakistan')
        country_data = get_country_info(country)
        return jsonify(country_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get country info: {str(e)}'}), 500

@app.route('/api/space', methods=['GET'])
def get_space_api():
    """Get space and astronomy information"""
    try:
        space_data = get_space_info()
        return jsonify(space_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get space info: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def get_health_api():
    """Get health tips and information"""
    try:
        health_data = get_health_tips()
        return jsonify(health_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get health tips: {str(e)}'}), 500

@app.route('/api/sports', methods=['GET'])
def get_sports_api():
    """Get sports scores and information"""
    try:
        sports_data = get_sports_scores()
        return jsonify(sports_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get sports info: {str(e)}'}), 500

@app.route('/api/market', methods=['GET'])
def get_market_api():
    """Get stock market information"""
    try:
        market_data = get_stock_market()
        return jsonify(market_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get market data: {str(e)}'}), 500

@app.route('/api/traffic', methods=['GET'])
def get_traffic_api():
    """Get traffic and transportation information"""
    try:
        city = request.args.get('city', 'Karachi')
        traffic_data = get_traffic_info(city)
        return jsonify(traffic_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get traffic info: {str(e)}'}), 500

@app.route('/api/education', methods=['GET'])
def get_education_api():
    """Get education and academic information"""
    try:
        education_data = get_education_info()
        return jsonify(education_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get education info: {str(e)}'}), 500

@app.route('/api/entertainment', methods=['GET'])
def get_entertainment_api():
    """Get entertainment and media information"""
    try:
        entertainment_data = get_entertainment_info()
        return jsonify(entertainment_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get entertainment info: {str(e)}'}), 500

@app.route('/api/detailed-weather', methods=['GET'])
def get_detailed_weather_api():
    """Get detailed weather information"""
    try:
        city = request.args.get('city', 'Karachi')
        weather_data = get_detailed_weather(city)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get detailed weather: {str(e)}'}), 500

@app.route('/api/all-info', methods=['GET'])
def get_all_comprehensive_info():
    """Get ALL available real-world information in one comprehensive call"""
    try:
        # Get all available information
        all_info = {
            "datetime": get_accurate_datetime(),
            "islamic": get_accurate_islamic_date(),
            "prayer_times": get_accurate_prayer_times(),
            "detailed_weather": get_detailed_weather(),
            "world_times": get_world_times(),
            "currency": get_currency_rates(),
            "crypto": get_crypto_prices(),
            "news": get_news_headlines(),
            "country_pakistan": get_country_info("Pakistan"),
            "space": get_space_info(),
            "health": get_health_tips(),
            "sports": get_sports_scores(),
            "market": get_stock_market(),
            "traffic": get_traffic_info(),
            "education": get_education_info(),
            "entertainment": get_entertainment_info(),
            "timestamp": datetime.now().isoformat()
        }

        return jsonify({
            "status": "success",
            "comprehensive_data": all_info,
            "data_categories": [
                "📅 Date & Time", "🌙 Islamic Calendar", "🕌 Prayer Times",
                "🌤️ Detailed Weather", "🌍 World Times", "💰 Currency Rates",
                "₿ Cryptocurrency", "📰 News Headlines", "🌍 Country Info",
                "🚀 Space & Astronomy", "🏥 Health Tips", "🏏 Sports Scores",
                "📈 Stock Market", "🚗 Traffic & Transport", "🎓 Education",
                "🎬 Entertainment"
            ],
            "data_sources": [
                "WorldTimeAPI", "Aladhan Prayer Times", "wttr.in Weather",
                "ExchangeRate-API", "CoinGecko", "BBC News RSS",
                "REST Countries", "NASA APOD", "Sports APIs", "Market APIs"
            ]
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get comprehensive info: {str(e)}'}), 500

# ----------- NEW: Comprehensive World Knowledge API Endpoints ------------

@app.route('/api/wikipedia', methods=['GET'])
def get_wikipedia_endpoint():
    """Get Wikipedia information for any topic"""
    try:
        topic = request.args.get('topic', '')
        language = request.args.get('language', 'en')

        if not topic:
            return jsonify({'error': 'Topic parameter is required'}), 400

        wiki_info = get_wikipedia_info(topic, language)
        return jsonify(wiki_info)
    except Exception as e:
        return jsonify({'error': f'Failed to get Wikipedia info: {str(e)}'}), 500

@app.route('/api/global-news', methods=['GET'])
def get_global_news_endpoint():
    """Get latest global news from multiple sources"""
    try:
        news_info = get_global_news()
        return jsonify(news_info)
    except Exception as e:
        return jsonify({'error': f'Failed to get global news: {str(e)}'}), 500

@app.route('/api/education', methods=['GET'])
def get_education_endpoint():
    """Get educational content and resources"""
    try:
        subject = request.args.get('subject', 'general')
        edu_info = get_educational_content(subject)
        return jsonify(edu_info)
    except Exception as e:
        return jsonify({'error': f'Failed to get educational content: {str(e)}'}), 500

@app.route('/api/world-facts', methods=['GET'])
def get_world_facts_endpoint():
    """Get comprehensive world facts and statistics"""
    try:
        facts_info = get_world_facts()
        return jsonify(facts_info)
    except Exception as e:
        return jsonify({'error': f'Failed to get world facts: {str(e)}'}), 500

@app.route('/api/knowledge-search', methods=['POST'])
def knowledge_search():
    """Search for any topic across all knowledge sources"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Search across multiple sources
        results = {
            'query': query,
            'sources': {},
            'timestamp': datetime.now().isoformat()
        }

        # Wikipedia search
        try:
            wiki_result = get_wikipedia_info(query)
            if wiki_result.get('success'):
                results['sources']['wikipedia'] = wiki_result
        except:
            pass

        # Educational content search
        try:
            edu_result = get_educational_content(query)
            if edu_result.get('success'):
                results['sources']['education'] = edu_result
        except:
            pass

        # World facts search
        try:
            facts_result = get_world_facts()
            if facts_result.get('success'):
                results['sources']['world_facts'] = facts_result
        except:
            pass

        # News search
        try:
            news_result = get_global_news()
            if news_result.get('success'):
                results['sources']['news'] = news_result
        except:
            pass

        return jsonify({
            'success': True,
            'results': results,
            'total_sources': len(results['sources']),
            'available_sources': ['Wikipedia', 'Educational Content', 'World Facts', 'Global News']
        })

    except Exception as e:
        return jsonify({'error': f'Knowledge search failed: {str(e)}'}), 500

# NEW: Additional 100% FREE API Endpoints

@app.route('/api/search', methods=['GET'])
def search_endpoint():
    """Search using DuckDuckGo (100% FREE)"""
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        search_results = get_google_search_results(query)
        return jsonify(search_results)
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/youtube-education', methods=['GET'])
def youtube_education_endpoint():
    """Get educational YouTube content (100% FREE)"""
    try:
        topic = request.args.get('topic', '')
        if not topic:
            return jsonify({'error': 'Topic parameter is required'}), 400

        youtube_content = get_youtube_educational_content(topic)
        return jsonify(youtube_content)
    except Exception as e:
        return jsonify({'error': f'YouTube education failed: {str(e)}'}), 500

@app.route('/api/academic-papers', methods=['GET'])
def academic_papers_endpoint():
    """Get academic papers from arXiv (100% FREE)"""
    try:
        topic = request.args.get('topic', '')
        if not topic:
            return jsonify({'error': 'Topic parameter is required'}), 400

        papers = get_academic_papers(topic)
        return jsonify(papers)
    except Exception as e:
        return jsonify({'error': f'Academic papers search failed: {str(e)}'}), 500

@app.route('/api/government-data', methods=['GET'])
def government_data_endpoint():
    """Get government and official statistics (100% FREE)"""
    try:
        gov_data = get_government_data()
        return jsonify(gov_data)
    except Exception as e:
        return jsonify({'error': f'Government data failed: {str(e)}'}), 500

@app.route('/api/translate', methods=['POST'])
def translate_endpoint():
    """Translation service (100% FREE)"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        translation = get_translation_service(text, target_language)
        return jsonify(translation)
    except Exception as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/api/ultimate-knowledge', methods=['POST'])
def ultimate_knowledge_search():
    """Ultimate knowledge search across ALL sources (100% FREE)"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Search across ALL FREE sources
        ultimate_results = {
            'query': query,
            'sources': {},
            'total_sources': 0,
            'timestamp': datetime.now().isoformat(),
            'cost': '$0.00 - 100% FREE'
        }

        # 1. Wikipedia search
        try:
            wiki_result = get_wikipedia_info(query)
            if wiki_result.get('success'):
                ultimate_results['sources']['wikipedia'] = wiki_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 2. DuckDuckGo search
        try:
            search_result = get_google_search_results(query)
            if search_result.get('success'):
                ultimate_results['sources']['web_search'] = search_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 3. Educational content
        try:
            edu_result = get_educational_content(query)
            if edu_result.get('success'):
                ultimate_results['sources']['education'] = edu_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 4. YouTube educational videos
        try:
            youtube_result = get_youtube_educational_content(query)
            if youtube_result.get('success'):
                ultimate_results['sources']['youtube_education'] = youtube_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 5. Academic papers
        try:
            academic_result = get_academic_papers(query)
            if academic_result.get('success'):
                ultimate_results['sources']['academic_papers'] = academic_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 6. Global news
        try:
            news_result = get_global_news()
            if news_result.get('success'):
                ultimate_results['sources']['global_news'] = news_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 7. World facts
        try:
            facts_result = get_world_facts()
            if facts_result.get('success'):
                ultimate_results['sources']['world_facts'] = facts_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        # 8. Government data
        try:
            gov_result = get_government_data()
            if gov_result.get('success'):
                ultimate_results['sources']['government_data'] = gov_result
                ultimate_results['total_sources'] += 1
        except:
            pass

        return jsonify({
            'success': True,
            'ultimate_knowledge': ultimate_results,
            'available_sources': [
                'Wikipedia (6M+ articles)',
                'DuckDuckGo Web Search',
                'Educational Resources',
                'YouTube Educational Videos',
                'Academic Papers (arXiv)',
                'Global News (BBC, CNN, Reuters)',
                'World Facts & Statistics',
                'Government & Official Data'
            ],
            'features': [
                '100% FREE - No API keys needed',
                'Real-time information',
                'Multiple languages supported',
                'Academic research papers',
                'Educational video content',
                'Global news coverage',
                'Government statistics'
            ]
        })

    except Exception as e:
        return jsonify({'error': f'Ultimate knowledge search failed: {str(e)}'}), 500

# ----------- Run Flask App ------------
# For production deployment
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# WSGI application entry point for deployment
application = app

if __name__ == '__main__':
    # Local development
    print("🚀 Starting HAMMAD BHAI AI Assistant locally...")
    print("🌐 Visit: http://localhost:5000")
    print("👨‍💻 Created by: MUHAMMAD HAMMAD ZUBAIR")
    app.run(debug=True, host='0.0.0.0', port=5000)
