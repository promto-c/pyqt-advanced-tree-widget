# Define example data
COLUMN_NAME_LIST = [
    'shot_id',
    'sequence',
    'status',
    'start_date',
    'due_date',
    'priority',
    'shot_length',
    'artist',
    'department',
]

ID_TO_DATA_DICT = {
    1: {
        'shot_id': 'SHOT001',
        'sequence': 'SEQ001',
        'status': 'In Progress',
        'start_date': '2023-06-17',
        'due_date': '2023-07-15',
        'priority': 2,
        'shot_length': 150,
        'artist': 'John Smith',
        'department': 'Compositing'
    },
    2: {
        'shot_id': 'SHOT002',
        'sequence': 'SEQ001',
        'status': 'Completed',
        'start_date': '2023-06-20',
        'due_date': '2023-07-10',
        'priority': 1,
        'shot_length': 200,
        'artist': 'Jane Doe',
        'department': 'Animation'
    },
    3: {
        'shot_id': 'SHOT003',
        'sequence': 'SEQ002',
        'status': 'Not Started',
        'start_date': '2023-06-25',
        'due_date': '2023-07-20',
        'priority': 3,
        'shot_length': 120,
        'artist': 'Alex Johnson',
        'department': 'Lighting'
    },
    4: {
        'shot_id': 'SHOT004',
        'sequence': 'SEQ002',
        'status': 'In Progress',
        'start_date': '2023-06-18',
        'due_date': '2023-07-25',
        'priority': 2,
        'shot_length': 180,
        'artist': 'Emily Brown',
        'department': 'Modeling'
    },
    5: {
        'shot_id': 'SHOT005',
        'sequence': 'SEQ003',
        'status': 'Completed',
        'start_date': '2023-06-22',
        'due_date': '2023-07-12',
        'priority': 1,
        'shot_length': 250,
        'artist': 'Michael Johnson',
        'department': 'Rigging'
    },
    6: {
        'shot_id': 'SHOT006',
        'sequence': 'SEQ003',
        'status': 'In Progress',
        'start_date': '2023-06-30',
        'due_date': '2023-07-30',
        'priority': 3,
        'shot_length': 130,
        'artist': 'Sophia Wilson',
        'department': 'Texturing'
    },
    7: {
        'shot_id': 'SHOT007',
        'sequence': 'SEQ004',
        'status': 'Not Started',
        'start_date': '2023-06-16',
        'due_date': '2023-07-18',
        'priority': 2,
        'shot_length': 160,
        'artist': 'Daniel Lee',
        'department': 'Animation'
    },
    8: {
        'shot_id': 'SHOT008',
        'sequence': 'SEQ004',
        'status': 'In Progress',
        'start_date': '2023-06-25',
        'due_date': '2023-07-25',
        'priority': 2,
        'shot_length': 190,
        'artist': 'Olivia Davis',
        'department': 'Compositing'
    },
    9: {
        'shot_id': 'SHOT009',
        'sequence': 'SEQ005',
        'status': 'In Progress',
        'start_date': '2023-06-19',
        'due_date': '2023-07-20',
        'priority': 3,
        'shot_length': 140,
        'artist': 'Noah Johnson',
        'department': 'Lighting'
    },
    10: {
        'shot_id': 'SHOT010',
        'sequence': 'SEQ005',
        'status': 'Completed',
        'start_date': '2023-06-20',
        'due_date': '2023-07-15',
        'priority': 1,
        'shot_length': 220,
        'artist': 'Isabella Clark',
        'department': 'Modeling'
    },
}
