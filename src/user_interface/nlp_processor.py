from typing import Dict, List, Tuple, Any, Optional
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re


class NLPProcessor:
    """Natural language processing module to understand user queries."""

    def __init__(self):
        """Initialize the NLP processor with required resources."""
        try:
            # Initialize NLTK resources (in production, we'd download these in a setup script)
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        except LookupError:
            # Fallback if NLTK resources aren't available
            self.stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'if', 'is', 'are'])
            print("Warning: NLTK resources not available. Using minimal stopwords.")
            
        # Define intent patterns
        self.intent_patterns = {
            "status_request": [
                r'(status|progress|update|how is|how are).*\b(project|task|work)\b',
                r'\b(what is|what\'s)\b.*(status|progress)',
                r'\b(give me|show|tell)\b.*(status|update|progress)'
            ],
            "forecast_request": [
                r'\b(forecast|prediction|estimate|predict|projected|future)\b',
                r'\b(when will|will.*complete|finish date|completion date)\b',
                r'\b(how long until|time to complete|expected duration)\b'
            ],
            "variance_explanation": [
                r'\b(why|explain|reason|cause).*(variance|different|discrepancy|off)\b',
                r'\b(variance|different|discrepancy|off).*(why|explain|reason|cause)\b',
                r'\b(why|what happened|what went wrong|what caused)\b'
            ],
            "recommendation_request": [
                r'\b(recommend|suggestion|advise|what should|how should|what can|how can)\b',
                r'\b(how to|best way to|options for|solutions for)\b',
                r'\b(what would you|steps to|action items|next steps)\b'
            ]
        }
        
        # Define entity extraction patterns
        self.entity_patterns = {
            "project_id": [
                r'\b(project|proj)\s*(id|number|#)?\s*[:=]?\s*([A-Za-z0-9-_]+)\b',
                r'\b([Pp][0-9]{3,4})\b'  # Match P001, p123, etc.
            ],
            "task_id": [
                r'\b(task|activity)\s*(id|number|#)?\s*[:=]?\s*([A-Za-z0-9-_]+)\b',
                r'\b([Tt][0-9]{3,4})\b'  # Match T001, t123, etc.
            ],
            "variance_type": [
                r'\b(cost|schedule|scope|performance)\s+(variance|discrepancy|difference|issue)\b',
                r'\b(variance|discrepancy|difference|issue)\s+in\s+(cost|schedule|scope|performance)\b',
                r'\b(CV|SV|CPI|SPI)\b'
            ],
            "date": [
                r'\b(as of|on|at|by)\s+([A-Za-z]+\s+[0-9]{1,2}(?:st|nd|rd|th)?(?:,\s+[0-9]{4})?)\b',
                r'\b([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})\b',
                r'\b(today|yesterday|tomorrow|next week|last week|next month|last month)\b'
            ]
        }

    def _preprocess_text(self, text: str) -> List[str]:
        """Tokenize, remove stopwords, and lemmatize text.
        
        Args:
            text: Input text to process
            
        Returns:
            List[str]: Processed tokens
        """
        # Tokenize and lowercase
        tokens = word_tokenize(text.lower())
        
        # Remove punctuation and numbers
        tokens = [token for token in tokens if token.isalpha()]
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Lemmatize tokens
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens

    def process_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Process a user query to identify intent and extract entities.
        
        Args:
            query: User's natural language query
            
        Returns:
            Tuple[str, Dict[str, Any]]: Identified intent and extracted entities
        """
        # Preprocess the query
        try:
            processed_tokens = self._preprocess_text(query)
        except Exception as e:
            # Fallback if preprocessing fails
            processed_tokens = query.lower().split()
            print(f"Warning: Error in preprocessing text: {e}")
        
        # Detect intent using patterns
        intent = self._detect_intent(query)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Look for specific keywords to enhance entity extraction
        keywords = {
            "cost": ["cost", "budget", "expense", "spending", "cpi", "cv", "acwp", "eac"],
            "schedule": ["schedule", "timeline", "deadline", "date", "spi", "sv", "bcws", "bcwp"]
        }
        
        # Check for variance type if it wasn't explicitly extracted
        if "variance_type" not in entities and any(kw in query.lower() for kw in keywords["cost"]):
            entities["variance_type"] = "cost"
        elif "variance_type" not in entities and any(kw in query.lower() for kw in keywords["schedule"]):
            entities["variance_type"] = "schedule"
        
        # Look for project names that might not match the ID pattern
        project_names = ["construction project", "software development", "it upgrade"]
        for name in project_names:
            if name.lower() in query.lower():
                entities["project_name"] = name
                # Assign a default project ID if none was extracted
                if "project_id" not in entities:
                    entities["project_id"] = "P001"  # Default project ID
                break
        
        return intent, entities

    def _detect_intent(self, query: str) -> str:
        """Detect the intent of a user query using pattern matching.
        
        Args:
            query: User's query
            
        Returns:
            str: Detected intent
        """
        # Convert to lowercase for easier matching
        query_lower = query.lower()
        
        # Check for matches with each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        # Default intent if no matches found
        return "unknown"

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from a user query using pattern matching.
        
        Args:
            query: User's query
            
        Returns:
            Dict[str, Any]: Extracted entities
        """
        entities = {}
        
        # Check for each entity type
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.search(pattern, query, re.IGNORECASE)
                if matches:
                    # Different patterns may have the entity in different groups
                    entity_value = None
                    for i in range(1, len(matches.groups()) + 1):
                        # Skip groups that are just qualifiers (like "project" in "project id")
                        if matches.group(i) not in ["project", "proj", "task", "activity", "id", "number", "#", 
                                                 "variance", "discrepancy", "difference", "issue", 
                                                 "in", "as of", "on", "at", "by"]:
                            entity_value = matches.group(i)
                            break
                    
                    if entity_value:
                        # Special handling for variance type
                        if entity_type == "variance_type":
                            if entity_value.upper() in ["CV", "CPI"]:
                                entity_value = "cost"
                            elif entity_value.upper() in ["SV", "SPI"]:
                                entity_value = "schedule"
                        
                        entities[entity_type] = entity_value
                        break  # Stop after first match for this entity type
        
        return entities

    def extract_project_info(self, query: str) -> Dict[str, str]:
        """Extract project-related information from a query.
        
        Args:
            query: User's query
            
        Returns:
            Dict[str, str]: Extracted project information
        """
        # This is a simplified version that could be enhanced with more sophisticated NLP
        info = {}
        
        # Extract project ID
        project_id_match = re.search(r'\b([Pp][0-9]{3,4})\b', query)
        if project_id_match:
            info["project_id"] = project_id_match.group(1)
        
        # Extract date ranges
        date_range_match = re.search(r'\b(from|between)\s+([A-Za-z0-9\s,/-]+)\s+(to|and)\s+([A-Za-z0-9\s,/-]+)\b', query)
        if date_range_match:
            info["start_date"] = date_range_match.group(2)
            info["end_date"] = date_range_match.group(4)
        
        return info

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate a simple embedding for a query (placeholder for real embedding).
        
        In a real implementation, this would use a language model or word embeddings.
        
        Args:
            query: User's query
            
        Returns:
            List[float]: A simple embedding vector
        """
        # This is just a placeholder - in a real implementation we would use a language model
        # Return a very simplified embedding based on presence of key terms
        embedding = [0.0] * 10
        
        terms = {
            "status": 0,
            "forecast": 1,
            "variance": 2,
            "recommendation": 3,
            "cost": 4,
            "schedule": 5,
            "project": 6,
            "task": 7,
            "performance": 8,
            "analysis": 9
        }
        
        query_lower = query.lower()
        for term, index in terms.items():
            if term in query_lower:
                embedding[index] = 1.0
        
        return embedding
