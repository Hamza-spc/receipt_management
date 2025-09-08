import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CategorizationService:
    def __init__(self):
        # Define category keywords
        self.category_keywords = {
            "Food & Dining": [
                "restaurant", "cafe", "coffee", "food", "dining", "pizza", "burger",
                "sandwich", "salad", "soup", "pasta", "chinese", "mexican", "italian",
                "fast food", "deli", "bakery", "grocery", "supermarket", "market"
            ],
            "Transportation": [
                "gas", "fuel", "gasoline", "petrol", "uber", "lyft", "taxi", "bus",
                "train", "metro", "subway", "parking", "toll", "highway", "airport"
            ],
            "Shopping": [
                "store", "shop", "retail", "clothing", "apparel", "shoes", "electronics",
                "amazon", "walmart", "target", "costco", "mall", "department"
            ],
            "Healthcare": [
                "pharmacy", "drug", "medicine", "medical", "doctor", "hospital",
                "clinic", "health", "prescription", "cvs", "walgreens"
            ],
            "Entertainment": [
                "movie", "cinema", "theater", "netflix", "spotify", "music", "game",
                "entertainment", "sports", "gym", "fitness", "club", "bar"
            ],
            "Utilities": [
                "electric", "water", "gas", "internet", "phone", "cable", "utility",
                "power", "heating", "cooling"
            ],
            "Office & Business": [
                "office", "supplies", "stationery", "business", "meeting", "conference",
                "printing", "copy", "fax"
            ],
            "Travel": [
                "hotel", "flight", "airline", "travel", "vacation", "trip", "booking",
                "reservation", "airbnb"
            ]
        }
    
    def categorize_item(self, item_name: str, merchant_name: Optional[str] = None) -> str:
        """Categorize an item based on its name and merchant"""
        text_to_analyze = f"{item_name} {merchant_name or ''}".lower()
        
        # Check for exact keyword matches
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    return category
        
        # Use pattern matching for common item types
        if self._is_food_item(item_name):
            return "Food & Dining"
        elif self._is_transportation_item(item_name):
            return "Transportation"
        elif self._is_shopping_item(item_name):
            return "Shopping"
        elif self._is_healthcare_item(item_name):
            return "Healthcare"
        elif self._is_entertainment_item(item_name):
            return "Entertainment"
        elif self._is_utility_item(item_name):
            return "Utilities"
        elif self._is_office_item(item_name):
            return "Office & Business"
        elif self._is_travel_item(item_name):
            return "Travel"
        
        return "Other"
    
    def categorize_receipt(self, receipt_data: Dict) -> Dict:
        """Categorize all items in a receipt"""
        merchant_name = receipt_data.get("merchant_name", "")
        items = receipt_data.get("items", [])
        
        categorized_items = []
        for item in items:
            item_name = item.get("item_name", "")
            category = self.categorize_item(item_name, merchant_name)
            
            categorized_item = item.copy()
            categorized_item["category"] = category
            categorized_items.append(categorized_item)
        
        return {
            **receipt_data,
            "items": categorized_items
        }
    
    def _is_food_item(self, item_name: str) -> bool:
        """Check if item is food-related"""
        food_patterns = [
            r'\b(burger|pizza|sandwich|salad|soup|pasta|rice|bread|meat|chicken|beef|fish)\b',
            r'\b(coffee|tea|juice|soda|water|beer|wine|alcohol)\b',
            r'\b(fruit|vegetable|apple|banana|orange|tomato|onion|potato)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in food_patterns)
    
    def _is_transportation_item(self, item_name: str) -> bool:
        """Check if item is transportation-related"""
        transport_patterns = [
            r'\b(gas|fuel|petrol|diesel|uber|lyft|taxi|bus|train|metro)\b',
            r'\b(parking|toll|highway|road|bridge|tunnel)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in transport_patterns)
    
    def _is_shopping_item(self, item_name: str) -> bool:
        """Check if item is shopping-related"""
        shopping_patterns = [
            r'\b(shirt|pants|dress|shoes|hat|jacket|clothing|apparel)\b',
            r'\b(phone|computer|laptop|tablet|electronics|gadget)\b',
            r'\b(book|magazine|newspaper|stationery|pen|pencil)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in shopping_patterns)
    
    def _is_healthcare_item(self, item_name: str) -> bool:
        """Check if item is healthcare-related"""
        health_patterns = [
            r'\b(medicine|drug|prescription|vitamin|supplement|bandage)\b',
            r'\b(doctor|medical|health|pharmacy|clinic|hospital)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in health_patterns)
    
    def _is_entertainment_item(self, item_name: str) -> bool:
        """Check if item is entertainment-related"""
        entertainment_patterns = [
            r'\b(movie|cinema|theater|netflix|spotify|music|game|gaming)\b',
            r'\b(sports|gym|fitness|club|bar|party|concert)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in entertainment_patterns)
    
    def _is_utility_item(self, item_name: str) -> bool:
        """Check if item is utility-related"""
        utility_patterns = [
            r'\b(electric|water|gas|internet|phone|cable|utility|power)\b',
            r'\b(heating|cooling|air conditioning|ac|heater)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in utility_patterns)
    
    def _is_office_item(self, item_name: str) -> bool:
        """Check if item is office-related"""
        office_patterns = [
            r'\b(office|supplies|stationery|pen|pencil|paper|printer|ink)\b',
            r'\b(meeting|conference|business|professional|work)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in office_patterns)
    
    def _is_travel_item(self, item_name: str) -> bool:
        """Check if item is travel-related"""
        travel_patterns = [
            r'\b(hotel|flight|airline|travel|vacation|trip|booking)\b',
            r'\b(reservation|airbnb|hostel|motel|luggage|suitcase)\b'
        ]
        return any(re.search(pattern, item_name.lower()) for pattern in travel_patterns)
