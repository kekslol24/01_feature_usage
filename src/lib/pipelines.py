'''
Pipelines for data extraction for feature usage analysis.
'''

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
        "name" :1,
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
        "anzahl_absenz": {"$sum": 1},
        "anzahl_joker_tage": {
            "$sum": {
                "$cond": [
                    {"$eq": ["$is_joker_day", True]},
                    1,
                    0
                ]
            }
        },
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
        "anzahl_absenz": 1,
        "anzahl_joker_tage": 1,
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
    "anzahl_notification": {"$sum": 1},
    "davon_chat_nachricht": {
    "$sum": {
        "$cond": [
            {"$eq": ["$is_chat", True]},
            1,
            0
        ]
    
    }
},
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
        "anzahl_notification": 1,
        "davon_chat_nachricht": 1,
        "_id": 1
    }}

]

event_pipe_meet = [
    {"$match": {
        "event_type": {"$eq": "meet"}
    }},
    {"$group": {
        "_id": "$school",
        "anzahl_meetings": {"$sum": 1}
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_meet"
    }},
    {"$project": {
        "name": "$school_meet.name",
        "anzahl_meetings": 1,
        "_id": 1
    }}
]

event_pipe_event = [
    {"$match": {
        "event_type": {"$eq": "event"}
    }},
    {"$group": {
        "_id": "$school",
        "anzahl_events": {"$sum": 1}
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_event"
    }},
    {"$project": {
        "name": "$school_event.name",
        "anzahl_events": 1,
        "_id": 1
    }}
]

file_pipe = [
    {"$group": {
        "_id": "$school",
        "anzahl_dateien": {"$sum": 1}
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_files"
    }},
    {"$project": {
        "name": "$school_files.name",
        "anzahl_dateien": 1,
        "_id": 1
    }}
]

question_pipe = [
    {"$group": {
        "_id": "$school",
        "anzahl_questions": {"$sum": 1}
    }},
    {"$lookup": {
        "from": "school",
        "localField": "_id",
        "foreignField": "_id",
        "as": "school_question"
    }},
    {"$project": {
        "name": "$school_question.name",
        "anzahl_questions": 1,
        "_id": 1
    }}
]

#################################################
# Pipeline list

pipeline_list = [
    (teacher_student_pipe, "school"), 
    (absence_pipe, "event"), 
    (message_pipe, "notification"), 
    (event_pipe_meet, "event"),
    (event_pipe_event, "event"),
    (file_pipe, "file"),
    (question_pipe, "question")]
