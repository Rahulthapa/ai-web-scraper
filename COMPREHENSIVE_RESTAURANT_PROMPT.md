# Comprehensive Restaurant Data Extraction Prompt

Use this prompt to extract **ALL** restaurant-related data including internal data, amenities, menu URLs, and everything else.

## 🎯 Complete Restaurant Extraction Prompt

Copy and paste this prompt into the AI prompt field:

```
Extract ALL restaurant data with complete internal information including:

BASIC INFORMATION:
- Restaurant name, description, tagline, slogan
- Website URL, social media links (Facebook, Instagram, Twitter)
- Business type, establishment type
- Year established, founding date

CONTACT DETAILS:
- Phone number (all formats: display, raw, international)
- Email address
- Contact form URL
- Reservation phone/email

LOCATION DATA:
- Full formatted address
- Street address, city, state, zip code, country
- GPS coordinates (latitude, longitude)
- Neighborhood, area, district
- Cross streets, landmarks
- Parking information, parking availability
- Public transit access

RATINGS & REVIEWS:
- Overall rating (1-5 stars)
- Review count (total reviews)
- Rating breakdown by category (food, service, ambiance, value)
- Best rating, worst rating
- Review sources (Yelp, Google, TripAdvisor, etc.)
- Recent review highlights

PRICING & COST:
- Price range ($, $$, $$$, $$$$)
- Average cost per person
- Menu price ranges
- Happy hour information
- Special offers, deals, discounts
- Group pricing, catering pricing

CUISINE & MENU:
- Cuisine types (all categories: American, Italian, Mexican, etc.)
- Food styles, cooking methods
- Dietary options (vegetarian, vegan, gluten-free, halal, kosher)
- Menu URL (all menu links: main menu, lunch menu, dinner menu, brunch menu, drinks menu, dessert menu)
- Online ordering URL
- Delivery menu URL
- Takeout menu URL
- Menu items (if available in data)
- Signature dishes, specialties
- Chef name, chef information

HOURS & AVAILABILITY:
- Opening hours (all days of week with times)
- Special hours (holidays, events)
- Happy hour times
- Brunch hours
- Kitchen hours vs. bar hours
- Last call times
- Closed days

AMENITIES & FEATURES:
- Wi-Fi availability
- Parking (valet, street, lot, garage)
- Outdoor seating, patio, terrace
- Indoor seating capacity
- Private dining rooms
- Event space, party rooms
- Bar area, lounge
- Live music, entertainment
- TV screens, sports viewing
- Wheelchair accessible
- High chairs, kid-friendly
- Pet-friendly, dog-friendly
- Dress code
- Noise level
- Ambiance (casual, formal, romantic, family-friendly)
- Good for groups, large parties
- Good for kids, families
- Romantic setting
- Business meetings
- Solo dining
- Date night
- Special occasions

SERVICES & OPTIONS:
- Reservations (accepted, required, online booking)
- Walk-ins accepted
- Takeout available
- Delivery available (all services: DoorDash, Uber Eats, Grubhub, etc.)
- Curbside pickup
- Drive-through
- Catering services
- Private events, parties
- Group dining
- Gift cards available
- Loyalty program, rewards

PAYMENT & TRANSACTIONS:
- Payment methods accepted (cash, credit cards, debit, mobile payments)
- Credit cards accepted (Visa, Mastercard, Amex, Discover)
- Mobile payment (Apple Pay, Google Pay, Samsung Pay)
- Cryptocurrency accepted
- Currencies accepted
- Tips accepted
- Split bills, separate checks

ATMOSPHERE & AMBIANCE:
- Noise level (quiet, moderate, loud)
- Lighting (dim, bright)
- Music type
- Crowd type (families, couples, business, tourists)
- Dress code (casual, smart casual, formal)
- Romantic, intimate setting
- Family-friendly
- Date night suitable
- Business lunch suitable

PHOTOS & MEDIA:
- Main image URL
- Photo gallery URLs
- Logo URL
- Menu images
- Interior photos
- Exterior photos
- Food photos
- All image URLs available

ADDITIONAL METADATA:
- Yelp ID, Yelp alias
- Google Place ID
- TripAdvisor ID
- OpenTable ID
- Foursquare ID
- Business owner information
- Management information
- Awards, recognition, certifications
- Health inspection ratings
- License information
- Insurance information

INTERNAL DATA:
- Any API data, JavaScript variables
- Internal IDs, database IDs
- Analytics data, tracking IDs
- Any other restaurant-related fields in the data

Return as a JSON array where each restaurant is a complete object with ALL available fields. Include every piece of information related to the restaurant, no matter how small or detailed. If a field is not available, omit it (don't include null values).
```

## 📋 Simplified Version (Shorter)

If the above is too long, use this shorter version:

```
Extract all restaurants with complete data including: name, address (full and parts), phone, email, website, GPS coordinates, rating, review count, cuisine types, price range, menu URLs (all types: main, lunch, dinner, brunch, drinks, online ordering, delivery), opening hours, amenities (Wi-Fi, parking, outdoor seating, wheelchair accessible, etc.), services (reservations, takeout, delivery, catering), payment methods, photos, social media links, and any other restaurant-related information available in the data. Return as a structured JSON array with all fields.
```

## 🎯 Ultra-Compact Version

For quick extraction:

```
Extract all restaurants with EVERY available detail: contact info, location (with coordinates), ratings, cuisine, pricing, ALL menu URLs, hours, amenities, services, payment options, photos, and any other restaurant data. Include internal data, API responses, and JavaScript variables if they contain restaurant information.
```

## 💡 Usage Tips

1. **For Paste HTML Mode:**
   - Paste the HTML
   - Use the comprehensive prompt above
   - The AI will extract everything it can find

2. **For Extract Internal Data Endpoint:**
   - Use `/extract-internal-data` with the URL
   - Add the prompt to extract structured data
   - This captures JavaScript variables and API responses

3. **For Regular URL Scraping:**
   - Enable "JavaScript rendering"
   - Use the comprehensive prompt
   - The scraper will extract embedded data + AI will structure it

## 🔍 What Gets Extracted

With this prompt, you'll get:

✅ **Basic Info** - Name, description, website  
✅ **Contact** - Phone, email, social media  
✅ **Location** - Full address, GPS, parking  
✅ **Ratings** - All rating sources and breakdowns  
✅ **Pricing** - Price range, deals, offers  
✅ **Cuisine** - All categories and dietary options  
✅ **Menus** - ALL menu URLs (main, lunch, dinner, brunch, drinks, delivery, online ordering)  
✅ **Hours** - Complete schedule, special hours  
✅ **Amenities** - Wi-Fi, parking, seating, accessibility  
✅ **Services** - Reservations, delivery, catering  
✅ **Payment** - All accepted methods  
✅ **Photos** - All image URLs  
✅ **Internal Data** - API responses, JavaScript variables  
✅ **Everything Else** - Any other restaurant-related data

## 📊 Example Output Structure

```json
[
  {
    "name": "Restaurant Name",
    "description": "...",
    "website": "https://...",
    "phone": "...",
    "email": "...",
    "address": "Full address",
    "address_parts": {
      "street": "...",
      "city": "...",
      "state": "...",
      "zip": "..."
    },
    "latitude": 29.7604,
    "longitude": -95.3698,
    "rating": 4.5,
    "review_count": 1234,
    "cuisine": ["Steakhouse", "American"],
    "price_range": "$$$",
    "menu_urls": {
      "main_menu": "https://...",
      "lunch_menu": "https://...",
      "dinner_menu": "https://...",
      "brunch_menu": "https://...",
      "drinks_menu": "https://...",
      "online_ordering": "https://...",
      "delivery_menu": "https://..."
    },
    "opening_hours": [...],
    "amenities": {
      "wifi": true,
      "parking": "valet",
      "outdoor_seating": true,
      "wheelchair_accessible": true
    },
    "services": {
      "reservations": true,
      "takeout": true,
      "delivery": ["DoorDash", "Uber Eats"],
      "catering": true
    },
    "payment_methods": ["Cash", "Credit Card", "Apple Pay"],
    "photos": [...],
    // ... all other fields
  }
]
```

---

**Note:** The more comprehensive the prompt, the more data the AI will extract. Use the full prompt for maximum data extraction!

