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
                    "type": "string",
                    "description": "Nazwa miasta w mianowniku, z polskimi znakami, np. Wrocław, Łódź, Kraków. Popraw pisownię, jeśli użytkownik pominął polskie znaki."
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
    },
{
        "type": "function",
        "name": "get_seats_map",
        "description": "Zwraca układ sali i zajęte miejsca dla wybranego seansu. Wywołaj po wyborze seansu przez użytkownika, zanim zapytasz o miejsca.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "screening_id": {
                    "type": "integer",
                }
            },
            "required": [
                "screening_id"
            ],
            "additionalProperties": False
        }
    },
{
        "type": "function",
        "name": "create_reservation",
        "description": "Sprawdza wolne czy miejsca są wolne natepnie robi rezerwację",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "screening_id": {
                    "type": "integer"
                },
                 "seats": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "row": {"type": "integer"},
                            "seat": {"type": "integer"}
                        },
                        "required": ["row", "seat"],
                        "additionalProperties": False
                    }
                },
                "guest_email": {
                    "type": ["string", "null"],
                },
                "guest_name": {
                    "type": ["string", "null"],
                }
            },
            "required": [
                "screening_id",
                "seats",
                "guest_email",
                "guest_name"
            ],
            "additionalProperties": False
        }
    }
]