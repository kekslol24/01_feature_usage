'''
Pipelines for data extraction for feature usage analysis.
'''

from src.lib import helpers
from datetime import datetime, timedelta

###########################################################################
HEUTE = datetime.now()
AKTUELLES_SCHULJAHR   = datetime(datetime.now().year, 7, 20)

VOR_30_TAGEN = HEUTE - timedelta(days=30)
VOR_30_TAGEN_PIPE = {"$gte": ["$created_at", VOR_30_TAGEN]}

VOR_90_TAGEN = HEUTE - timedelta(days=90)
VOR_90_TAGEN_PIPE = {"$gte": ["$created_at", VOR_90_TAGEN]}

schuljahresende_dieses_jahr = datetime(HEUTE.year, 7, 20)

if HEUTE > schuljahresende_dieses_jahr:
    LETZTES_SCHULJAHR_START = datetime(HEUTE.year -1 , 8, 1)
    LETZTES_SCHULJAHR_ENDE = datetime(HEUTE.year , 7, 20)
else:
    LETZTES_SCHULJAHR_START = datetime(HEUTE.year -2, 8, 1)
    LETZTES_SCHULJAHR_ENDE = datetime(HEUTE.year -1, 7, 20)

# LETZTES_SCHULJAHR_START = datetime(datetime.now().year - 1, 8, 1)
# LETZTES_SCHULJAHR_ENDE = datetime(datetime.now().year, 7, 20)
LETZTES_SCHULJAHR_PIPE = {"$and": [{"$gte": ["$created_at", LETZTES_SCHULJAHR_START]}, {"$lte": ["$created_at", LETZTES_SCHULJAHR_ENDE]}]}
###########################################################################
pipe_dict = {"30_tage": VOR_30_TAGEN_PIPE, "90_tage": VOR_90_TAGEN_PIPE, "letztes_schuljahr": LETZTES_SCHULJAHR_PIPE}

# chat_pipe_dict = {}

# for suffix, condition in pipe_dict.items():
#     chat_pipe_dict[suffix] = {"$and": [condition, {"$eq": ["$is_chat", True]}]}      ----> because we append new values to the pipe_dict
                                                                                        # it is no longer necessary
###########################################################################

teacher_student_pipe = [
    {"$match": {
        "deleted_at": {"$eq": None}
    }},
    {"$lookup": {
        "from": "user",
        "localField": "teachers",
        "foreignField": "_id",
        "as": "school_teachers"
    }},
    {"$lookup": {
        "from": "student",
        "localField": "_id",
        "foreignField": "school",
        "as": "school_students"     ### muss anderen namen haben, da sonst dieses lookup das vorherige überschreibt
    }},
    {"$project": {
        "name" : 1,
        "anzahl_aktive_lehrer": {
        "$size": {
            "$filter": {
                "input": "$school_teachers",
                "as": "st",
                "cond": {"$ne": ["$$st.is_deleted", True]}
                }
            }
        },
        "anzahl_aktive_schüler": {
            "$size": {
                "$filter": {
                    "input": "$school_students",
                    "as": "s",
                    "cond": {"$eq": ["$$s.deleted_at", None]}
                }
            }
        },
        "created_at": 1,
        "_id": 1
    }},
    # {"$sort": {
    #     "anzahl_aktive_lehrer": -1}}
]

absence_pipe = [
    {"$match": {
        "event_type": {"$eq": "absence"},
        # "created_at": {"$gte": datetime(2026, 6, 1), "$lt": datetime(2026, 6, 30)}
    }},
    # {"$limit": 5},
    {"$group": {
        "_id": "$school",
        "anzahl_absenz_historie": {"$sum": 1},
        "anzahl_joker_tage_historie": {
            "$sum": {
                "$cond": [
                    {"$eq": ["$is_joker_day", True]},
                    1,
                    0
                ]
            }
        },
        **helpers.timeframe_fields("absenz", pipe_dict),
        **helpers.timeframe_fields("joker_tage", pipe_dict)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_info"
    }},
    {"$unwind": "$school_info"},
    {"$project": {
        "joker_tage_aktiviert": {
            "$cond": [
                {"$eq": ["$school_info.joker_days_enabled", True]},
                "Aktiviert",
                "Nicht Aktiviert"
    ]
},
        # "$school_info.client_name": 1
        "name": "$school_info.name",
        "anzahl_absenz_30_tage": 1, 
        "anzahl_absenz_90_tage": 1,
        "anzahl_absenz_letztes_schuljahr": 1,
        "anzahl_absenz_historie": 1,
        "anzahl_joker_tage_historie": 1,
        "_id": 1
    # }},
    # {"$sort": {
    #     "anzahl_absenz": -1
    }},
    # {"$sort": {
    #     "anzahl_joker_tage": 1,
    #     "joker_tage_aktiviert": 1}}
    
]

message_pipe = [
    {"$group": {
    "_id": "$school",
    "anzahl_notification_historie": {"$sum": 1},
    "davon_chat_nachricht_historie": {
    "$sum": {
        "$cond": [
            {"$eq": ["$is_chat", True]},
            1,
            0
        ]
    }
},
    **helpers.timeframe_fields("nachrichten", pipe_dict),
    **helpers.timeframe_fields("chat_nachrichten", helpers.cond_cat("is_chat", True, pipe_dict))
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_notification"
    }},
    {"$unwind": "$school_notification"},
    {"$project": {
        "name": "$school_notification.name",
        "anzahl_nachrichten_30_tage": 1,
        "anzahl_nachrichten_90_tage": 1,
        "anzahl_nachrichten_letztes_schuljahr": 1,
        "anzahl_notification_historie": 1,
        "anzahl_chat_nachrichten_30_tage": 1,
        "anzahl_chat_nachrichten_90_tage": 1,
        "anzahl_chat_nachrichten_letztes_schuljahr": 1,
        "anzahl_chat_nachrichten_historie": 1,
        "_id": 1
    }}

]

event_pipe_meet = [
    {"$match": {
        "event_type": {"$eq": "meet"}
    }},
    {"$group": {
        "_id": "$school",
        "anzahl_meetings_historie": {"$sum": 1},
        **helpers.timeframe_fields("meetings", pipe_dict)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_meet"
    }},
    {"$project": {
        "name": "$school_meet.name",
        "anzahl_meetings_30_tage": 1,
        "anzahl_meetings_90_tage": 1,
        "anzahl_meetings_letztes_schuljahr": 1,
        "anzahl_meetings_historie": 1,
        "_id": 1
    }}
]

event_pipe_event = [
    {"$match": {
        "event_type": {"$eq": "event"}
    }},
    {"$group": {
        "_id": "$school",
        "anzahl_events_historie": {"$sum": 1},
        **helpers.timeframe_fields("events", pipe_dict)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_event"
    }},
    {"$project": {
        "name": "$school_event.name",
        "anzahl_events_30_tage": 1,
        "anzahl_events_90_tage": 1,
        "anzahl_events_letztes_schuljahr": 1,
        "anzahl_events_historie": 1,
        "_id": 1
    }}
]

event_pipe_category = [{
    "$group": {
        "_id": "$school",
        "event_event_historie": {
            "$sum": {
                "$cond": [{"$eq": ["$event_category", "event"]}, 1, 0]}
        },
        "holiday_event_historie": {
            "$sum": {
                "$cond": [{"$eq": ["$event_category", "holiday"]}, 1,0]}
        },
        "task_event_historie": {
            "$sum": {
                "$cond": [{"$eq": ["$event_category", "task"]}, 1, 0]}
        },
        "test_event_historie": {
            "$sum": {
                "$cond": [{"$eq": ["$event_category", "test"]}, 1, 0]}
        },
        **helpers.timeframe_fields("event_event", helpers.cond_cat("event_category", "event", pipe_dict)),
        **helpers.timeframe_fields("holiday_event", helpers.cond_cat("event_category", "holiday", pipe_dict)),
        **helpers.timeframe_fields("task_event", helpers.cond_cat("event_category", "task", pipe_dict)),
        **helpers.timeframe_fields("test_event", helpers.cond_cat("event_category", "test", pipe_dict))
        }
    }
]


file_pipe = [
    {"$group": {
        "_id": "$school",
        "anzahl_dateien_historie": {"$sum": 1},
        **helpers.timeframe_fields("files", pipe_dict)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_files"
    }},
    {"$project": {
        "name": "$school_files.name",
        "anzahl_files_30_tage": 1,
        "anzahl_files_90_tage": 1,
        "anzahl_files_letztes_schuljahr": 1,
        "anzahl_dateien_historie": 1,
        "_id": 1
    }}
]

question_pipe = [
    {"$group": {
        "_id": "$school",
        "anzahl_questions_historie": {"$sum": 1},
        **helpers.timeframe_fields("questions", pipe_dict)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_question"
    }},
    {"$project": {
        "name": "$school_question.name",
        "anzahl_questions_30_tage": 1,
        "anzahl_questions_90_tage": 1,
        "anzahl_questions_letztes_schuljahr": 1,
        "anzahl_questions_historie": 1,
        "_id": 1
    }}
]

status_pipe = [{
    "$project": {
        "loeschstatus": {
        "$cond":[{"$ne": ["$deleted_at", None]},
                "$deleted_at",
                None]
        },
        "kuendigungsstatus": {
            "$cond": [{"$ne": ["$invoicing_cancellation_date", None]},
                        "$invoicing_cancellation_date",
                        None]
        },
        "status": {
            "$cond": [{"$eq": ["$deactivated", True]},
                        "Deaktiviert",
                        "Aktiv"]
        },
        "_id": 1
    }
}
]

money_pipe = [{
    "$group": {
        "_id": "$school_id",
        "anzahl_invoices_historie": {"$sum": "$amount"},
        **helpers.timeframe_fields("invoices", pipe_dict, is_money=True)
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_total"
    }},
    {"$unwind": "$school_total"},
    {"$project": {
        "_id": 1,
        "anzahl_invoices_historie": 1,
        "invoicing_start_date": "$school_total.invoicing_start_date",
        "invoicing_cancellation_date": "$school_total.invoicing_cancellation_date",
        "anzahl_invoices_30_tage": 1,
        "anzahl_invoices_90_tage": 1,
        "anzahl_invoices_letztes_schuljahr": 1,
        "anzahl_invoices_historie": 1,
    }
}]


#################################################
# Pipeline list

pipeline_list = [
    (teacher_student_pipe, "school"), 
    (absence_pipe, "event"), 
    (message_pipe, "notification"), 
    (event_pipe_meet, "event"),
    (event_pipe_event, "event"),
    (event_pipe_category, "event"),
    (file_pipe, "file"),
    (question_pipe, "question"),
    (status_pipe, "school"),
    (money_pipe, "invoices")
    ]
