from typing import Dict, Any, List
import os
import json
import logging
import re

logger = logging.getLogger(__name__)


class AIFilter:
    """
    AI-powered data filter and extractor.
    Supports multiple AI providers:
    - Google Gemini (FREE tier available)
    - OpenAI GPT (paid)
    - Fallback to smart extraction (no API needed)
    """
    
    def __init__(self, api_key: str = None):
        self.gemini_api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = None
        self._init_ai_provider()
    
    def _init_ai_provider(self):
        """Initialize the best available AI provider"""
        # Try Google Gemini first (FREE tier)
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.provider = "gemini"
                logger.info("AI Filter initialized with Google Gemini")
                return
            except ImportError:
                logger.warning("google-generativeai not installed, trying OpenAI")
            except Exception as e:
                logger.warning(f"Failed to init Gemini: {e}")
        
        # Try OpenAI as fallback
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                self.provider = "openai"
                logger.info("AI Filter initialized with OpenAI")
                return
            except ImportError:
                logger.warning("openai not installed")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}")
        
        # Fallback to smart extraction (no API needed)
        self.provider = "smart_extraction"
        logger.info("AI Filter using smart extraction (no API)")

    async def filter_and_structure(
        self,
        data: Dict[str, Any],
        prompt: str = None
    ) -> List[Dict[str, Any]]:
        """
        Use AI to filter and structure scraped data based on user prompt.
        
        Args:
            data: Raw scraped data from the web page
            prompt: User's instruction for what to extract (e.g., "Extract all product names and prices")
        
        Returns:
            List of structured data items matching the prompt
        """
        if not prompt:
            return [data]
        
        try:
            if self.provider == "gemini":
                return await self._filter_with_gemini(data, prompt)
            elif self.provider == "openai":
                return await self._filter_with_openai(data, prompt)
            else:
                return await self._smart_extraction(data, prompt)
        except Exception as e:
            logger.error(f"AI filtering failed: {e}")
            # Return original data on failure
            return [data]

    async def _filter_with_gemini(self, data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """Use Google Gemini to extract data"""
        try:
            # Prepare the content for AI
            content_text = self._prepare_content(data)
            
            ai_prompt = f"""You are a data extraction assistant. Analyze the following web page content and extract information based on the user's request.

USER REQUEST: {prompt}

WEB PAGE CONTENT:
{content_text}

INSTRUCTIONS:
1. Extract ONLY the information that matches the user's request
2. Return the data as a JSON array of objects
3. Each object should have relevant key-value pairs
4. If no matching data is found, return an empty array []
5. Be precise and include all matching items

Return ONLY valid JSON, no explanations or markdown. Example format:
[{{"name": "Item 1", "price": "$10"}}, {{"name": "Item 2", "price": "$20"}}]

JSON OUTPUT:"""

            response = self.model.generate_content(ai_prompt)
            result_text = response.text.strip()
            
            # Clean up the response (remove markdown code blocks if present)
            result_text = self._clean_json_response(result_text)
            
            # Parse JSON response
            try:
                extracted = json.loads(result_text)
                if isinstance(extracted, list):
                    return extracted if extracted else [data]
                else:
                    return [extracted]
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Gemini response as JSON: {result_text[:200]}")
                return [{"ai_extracted": result_text, "original_url": data.get("url")}]
                
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            raise

    async def _filter_with_openai(self, data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """Use OpenAI GPT to extract data"""
        try:
            content_text = self._prepare_content(data)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Extract information from web content and return it as JSON."
                    },
                    {
                        "role": "user",
                        "content": f"""Extract the following from this web page:

REQUEST: {prompt}

CONTENT:
{content_text}

Return ONLY a JSON array of extracted items. No explanations."""
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = self._clean_json_response(result_text)
            
            try:
                extracted = json.loads(result_text)
                if isinstance(extracted, list):
                    return extracted if extracted else [data]
                else:
                    return [extracted]
            except json.JSONDecodeError:
                return [{"ai_extracted": result_text, "original_url": data.get("url")}]
                
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {e}")
            raise

    async def _smart_extraction(self, data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """
        Smart extraction without AI API.
        Uses keyword matching and pattern recognition.
        """
        prompt_lower = prompt.lower()
        result = {"url": data.get("url"), "title": data.get("title")}
        
        # Extract based on common patterns in the prompt
        if any(word in prompt_lower for word in ["price", "cost", "dollar", "$"]):
            result["prices"] = self._extract_prices(data)
        
        if any(word in prompt_lower for word in ["email", "contact", "mail"]):
            result["emails"] = self._extract_emails(data)
        
        if any(word in prompt_lower for word in ["phone", "number", "call", "tel"]):
            result["phones"] = self._extract_phones(data)
        
        if any(word in prompt_lower for word in ["link", "url", "href"]):
            result["links"] = data.get("links", [])[:20]
        
        if any(word in prompt_lower for word in ["image", "picture", "photo", "img"]):
            result["images"] = data.get("images", [])[:20]
        
        if any(word in prompt_lower for word in ["heading", "title", "h1", "h2"]):
            result["headings"] = data.get("headings", {})
        
        if any(word in prompt_lower for word in ["table", "data", "list"]):
            result["tables"] = data.get("tables", [])
            result["lists"] = data.get("lists", [])
        
        # If nothing specific matched, return text content
        if len(result) <= 2:
            result["text_content"] = data.get("text_content", "")[:5000]
            result["main_content"] = data.get("main_content", "")
        
        return [result]

    def _prepare_content(self, data: Dict[str, Any]) -> str:
        """Prepare web page content for AI processing"""
        parts = []
        
        if data.get("title"):
            parts.append(f"TITLE: {data['title']}")
        
        if data.get("meta_tags"):
            desc = data["meta_tags"].get("description", "")
            if desc:
                parts.append(f"DESCRIPTION: {desc}")
        
        if data.get("headings"):
            for level, texts in data["headings"].items():
                for text in texts[:5]:  # Limit headings
                    parts.append(f"{level.upper()}: {text}")
        
        if data.get("main_content"):
            # Limit content size for API
            parts.append(f"CONTENT: {data['main_content'][:8000]}")
        elif data.get("text_content"):
            parts.append(f"CONTENT: {data['text_content'][:8000]}")
        
        if data.get("tables"):
            for i, table in enumerate(data["tables"][:3]):
                parts.append(f"TABLE {i+1}: {json.dumps(table[:10])}")
        
        if data.get("lists"):
            for i, lst in enumerate(data["lists"][:5]):
                parts.append(f"LIST {i+1}: {json.dumps(lst[:10])}")
        
        return "\n\n".join(parts)

    def _clean_json_response(self, text: str) -> str:
        """Clean AI response to extract valid JSON"""
        # Remove markdown code blocks
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()
        return text

    def _extract_prices(self, data: Dict[str, Any]) -> List[str]:
        """Extract price patterns from text"""
        text = data.get("text_content", "") + " " + data.get("main_content", "")
        # Match common price patterns
        patterns = [
            r'\$[\d,]+\.?\d*',  # $10, $10.99, $1,000
            r'[\d,]+\.?\d*\s*(?:USD|dollars?)',  # 10 USD, 10 dollars
            r'(?:Rs\.?|₹)\s*[\d,]+\.?\d*',  # Rs. 100, ₹100
            r'€[\d,]+\.?\d*',  # €10
            r'£[\d,]+\.?\d*',  # £10
        ]
        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend(matches)
        return list(set(prices))[:20]

    def _extract_emails(self, data: Dict[str, Any]) -> List[str]:
        """Extract email addresses from text"""
        text = data.get("text_content", "") + " " + str(data.get("links", []))
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, text)
        return list(set(emails))[:20]

    def _extract_phones(self, data: Dict[str, Any]) -> List[str]:
        """Extract phone numbers from text"""
        text = data.get("text_content", "")
        patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+\d{1,3}[-.\s]?\d{4,14}',  # International
        ]
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        return list(set(phones))[:20]
