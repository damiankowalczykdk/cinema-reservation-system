from enum import Enum

from openai.types.responses import FunctionToolParam


class Genre(Enum):
    ACTION = "action"
    COMEDY = "comedy"
    DRAMA = "drama"
    HORROR = "horror"
    THRILLER = "thriller"
    ROMANCE = "romance"
    SCI_FI = "sci_fi"
    FANTASY = "fantasy"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"
    CRIME = "crime"
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    FAMILY = "family"
    WAR = "war"


TOOLS: list[FunctionToolParam] = [
    {
        "type": "function",
        "name": "search_showtimes",
        "description": "Znajduje seanse filmowe spełniające wymagania użytkownika.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string"
                },
                "genre": {
                    "type": ["string", "null"],
                    "enum": [g.value for g in Genre] + [None]
                },
                "after": {
                    "type": ["string", "null"],
                    "description": "Najwcześniejsza data i godzina seansu w formacie ISO 8601, np. 2026-10-07T19:00:00+02:00. Null, jeśli użytkownik nie podał pory."
                },
                "before": {
                    "type": ["string", "null"],
                    "description": "Najpozniejsza data i godzina seansu w formacie ISO 8601, np. 2026-10-07T19:00:00+02:00. Null, jeśli użytkownik nie podał pory. gdy użytkownik pyta o konkretny dzień, after to początek tego dnia (00:00), a before to początek następnego."
                }
            },
            "required": [
                "city",
                "genre",
                "after",
                "before",
            ],
            "additionalProperties": False
        }
    }
]