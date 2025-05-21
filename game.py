# Campus Treasure Hunt
# A text-based adventure game where players search for lost notes in a virtual campus

import json
import os
import time
from datetime import datetime
from enum import Enum

# Game configuration
GAME_VERSION = "1.2.0"
SAVE_FILE = "game_save.json"
DIFFICULTY_LEVELS = {
    'easy': {'time_limit': 0, 'hints': 3, 'score_multiplier': 1.0},
    'normal': {'time_limit': 600, 'hints': 2, 'score_multiplier': 1.5},
    'hard': {'time_limit': 300, 'hints': 1, 'score_multiplier': 2.0}
}

# Game states
class GameState(Enum):
    CONTINUE = 'continue'
    WIN = 'win'
    LOSE = 'lose'
    QUIT = 'quit'
    ACCESS_DENIED = 'access_denied'
    SPECIAL_EVENT = 'special_event'
    HINT_ACTIVATED = 'hint_activated'

# Achievement types
class AchievementType(Enum):
    ENTERED_CAMPUS = 'entered_campus'
    ENTERED_LIBRARY = 'entered_library'
    FOUND_NOTES = 'found_notes'
    COLLECTED_ALL_ITEMS = 'collected_all_items'
    VISITED_ALL_LOCATIONS = 'visited_all_locations'
    COMPLETED_UNDER_TIME = 'completed_under_time'
    NO_HINTS_USED = 'no_hints_used'
    EXPLORED_QUAD = 'explored_quad'
    VISITED_MUSEUM = 'visited_museum'
    ATTENDED_LECTURE = 'attended_lecture'
    ENGINEERING_MASTER = 'engineering_master'
    SCIENCE_EXPLORER = 'science_explorer'
    TEACHING_PIONEER = 'teaching_pioneer'
    NOBEL_POTENTIAL = 'nobel_potential'
    SOCIAL_BUTTERFLY = 'social_butterfly'

# Item types
class ItemType(Enum):
    ACCESS = 'access'  # Access control items
    INFO = 'info'      # Information/guide items
    COLLECTIBLE = 'collectible'  # Collection/achievement items
    FUN = 'fun'        # Fun/immersion items
    QUEST = 'quest'    # Quest chain items

# Game map data
map_data = {
    'University Entrance': {
        'DESCRIPTION': "You are at the main entrance of the University of Sydney. The iconic Quadrangle stands before you. A security guard is checking student IDs at the gate.",
        'EXITS': {'north': 'Quadrangle', 'east': 'Wentworth Building', 'west': 'Fisher Library'},
        'ITEMS': ['student_card'],
        'SPECIAL': {
            'student_card': {
                'description': "Your University of Sydney student ID card with your name and student number.",
                'required': True,
                'usage': "Required for access to university facilities",
                'type': ItemType.ACCESS
            }
        },
        'ACCESS_CONTROL': {
            'required_items': ['student_card'],
            'denied_message': "The security guard stops you: 'I'm sorry, you need a valid student ID to enter the university.'"
        }
    },
    'Quadrangle': {
        'DESCRIPTION': "You are in the Main Quadrangle, the heart of the university. The Great Hall stands to the north, with MacLaurin Hall to the east. The old sandstone walls surround you.",
        'EXITS': {'north': 'Great Hall', 'east': 'MacLaurin Hall', 'south': 'University Entrance', 'west': 'Fisher Library'},
        'ITEMS': ['lecture_notes', 'university_guide', 'mysterious_note'],
        'SPECIAL': {
            'lecture_notes': {
                'description': "Some lecture notes from a previous class.",
                'required': False,
                'usage': "Contains useful academic information",
                'type': ItemType.INFO
            },
            'mysterious_note': {
                'description': "A torn piece of paper clinging to the sandstone wall. It seems to have been here for a while.",
                'required': False,
                'usage': "Read the mysterious note",
                'type': ItemType.QUEST
            }
        },
        'ACCESS_CONTROL': {
            'required_items': ['student_card'],
            'denied_message': "The security guard stops you: 'I'm sorry, you need a valid student ID to enter the university.'"
        }
    },
    'Great Hall': {
        'DESCRIPTION': "You are in the magnificent Great Hall, with its beautiful stained glass windows and grand architecture.",
        'EXITS': {'south': 'Quadrangle'},
        'ITEMS': ['graduation_gown'],
        'SPECIAL': {
            'graduation_gown': {
                'description': "A graduation gown, symbolizing academic achievement.",
                'required': False,
                'usage': "Worn during graduation ceremonies"
            }
        }
    },
    'MacLaurin Hall': {
        'DESCRIPTION': "You are in MacLaurin Hall, known for its impressive architecture and academic atmosphere.",
        'EXITS': {'west': 'Quadrangle', 'east': 'Chau Chak Wing Museum'},
        'ITEMS': ['library_card'],
        'SPECIAL': {
            'library_card': {
                'description': "A library access card for Fisher Library.",
                'required': True,
                'usage': "Required to access Fisher Library"
            }
        }
    },
    'Chau Chak Wing Museum': {
        'DESCRIPTION': "You are in the Chau Chak Wing Museum, home to the university's art and antiquities collections.",
        'EXITS': {'west': 'MacLaurin Hall'},
        'ITEMS': ['museum_guide', ''
                                  ''
                                  'ancient_artifact'],
        'SPECIAL': {
            'museum_guide': {
                'description': "A guide to the museum's collections.",
                'required': False,
                'usage': "Helps understand museum exhibits"
            }
        }
    },
    'Fisher Library': {
        'DESCRIPTION': "You are in Fisher Library, the main university library. A 'lost COMP9001 notes' lies on a study desk.",
        'EXITS': {'east': 'Quadrangle', 'south': 'University Entrance', 'north': 'Law Library'},
        'ITEMS': ['COMP9001 notes', 'textbook', 'research_paper'],
        'SPECIAL': {
            'COMP9001 notes': {
                'description': "The lost COMP9001 notes you've been searching for.",
                'required': True,
                'usage': "Contains important course material"
            }
        }
    },
    'Law Library': {
        'DESCRIPTION': "You are in the Law Library, a quiet space for legal research.",
        'EXITS': {'south': 'Fisher Library'},
        'ITEMS': ['law_book'],
        'SPECIAL': {
            'law_book': {
                'description': "A comprehensive law textbook.",
                'required': False,
                'usage': "Contains legal information"
            }
        }
    },
    'Wentworth Building': {
        'DESCRIPTION': "You are in the Wentworth Building, home to student services and food outlets.",
        'EXITS': {'west': 'University Entrance', 'north': 'Manning House'},
        'ITEMS': ['student_discount_card', 'cafeteria_menu', 'campus_map'],
        'SPECIAL': {
            'student_discount_card': {
                'description': "A card offering student discounts at campus outlets.",
                'required': False,
                'usage': "Gives access to student discounts"
            },
            'campus_map': {
                'description': "A detailed map of the University of Sydney campus.",
                'required': False,
                'usage': "Helps navigate the campus",
                'type': ItemType.INFO
            }
        }
    },
    'Manning House': {
        'DESCRIPTION': "You are in Manning House, a hub for student activities and organizations.",
        'EXITS': {'south': 'Wentworth Building'},
        'ITEMS': ['club_membership'],
        'SPECIAL': {
            'club_membership': {
                'description': "A membership card for a student club.",
                'required': False,
                'usage': "Gives access to club activities"
            }
        }
    },
    'Engineering Precinct': {
        'DESCRIPTION': "You are in the Engineering Precinct, surrounded by the Peter Nicol Russell Building and Aeronautical Engineering Building.",
        'EXITS': {'north': 'PNR Building', 'east': 'Electrical Engineering Building', 'south': 'University Entrance'},
        'ITEMS': ['engineering_drawing', 'safety_goggles'],
        'SPECIAL': {
            'safety_goggles': {
                'description': "Safety goggles required for engineering labs.",
                'required': False,
                'usage': "Protects eyes in engineering labs"
            }
        }
    },
    'PNR Building': {
        'DESCRIPTION': "You are in the Peter Nicol Russell Building, home to mechanical engineering.",
        'EXITS': {'south': 'Engineering Precinct'},
        'ITEMS': ['mechanical_tools'],
        'SPECIAL': {
            'mechanical_tools': {
                'description': "A set of precision mechanical tools.",
                'required': False,
                'usage': "Used in mechanical engineering projects"
            }
        }
    },
    'Electrical Engineering Building': {
        'DESCRIPTION': "You are in the Electrical Engineering Building, filled with advanced electronics labs.",
        'EXITS': {'west': 'Engineering Precinct'},
        'ITEMS': ['circuit_board'],
        'SPECIAL': {
            'circuit_board': {
                'description': "A prototype circuit board.",
                'required': False,
                'usage': "Used in electronics projects"
            }
        }
    },
    'Science Precinct': {
        'DESCRIPTION': "You are in the Science Precinct, surrounded by the Chemistry, Physics, and Madsen Buildings.",
        'EXITS': {'north': 'Chemistry Building', 'east': 'Physics Building', 'west': 'Madsen Building'},
        'ITEMS': ['lab_coat', 'scientific_calculator'],
        'SPECIAL': {
            'lab_coat': {
                'description': "A white lab coat required for science experiments.",
                'required': False,
                'usage': "Protects clothing in laboratories"
            }
        }
    },
    'Chemistry Building': {
        'DESCRIPTION': "You are in the Chemistry Building, filled with laboratories and research facilities.",
        'EXITS': {'south': 'Science Precinct'},
        'ITEMS': ['chemical_notes'],
        'SPECIAL': {
            'chemical_notes': {
                'description': "Notes from a chemistry experiment.",
                'required': False,
                'usage': "Contains chemical formulas and procedures"
            }
        }
    },
    'Physics Building': {
        'DESCRIPTION': "You are in the Physics Building, home to advanced physics research and teaching.",
        'EXITS': {'west': 'Science Precinct'},
        'ITEMS': ['physics_textbook'],
        'SPECIAL': {
            'physics_textbook': {
                'description': "A comprehensive physics textbook.",
                'required': False,
                'usage': "Contains physics theories and formulas"
            }
        }
    },
    'Madsen Building': {
        'DESCRIPTION': "You are in the Madsen Building, known for its biological sciences research.",
        'EXITS': {'east': 'Science Precinct'},
        'ITEMS': ['microscope_slides'],
        'SPECIAL': {
            'microscope_slides': {
                'description': "A set of prepared microscope slides.",
                'required': False,
                'usage': "Used for biological observations"
            }
        }
    },
    'New Law Building': {
        'DESCRIPTION': "You are in the New Law Building, a modern facility for legal education.",
        'EXITS': {'south': 'University Entrance'},
        'ITEMS': ['legal_casebook'],
        'SPECIAL': {
            'legal_casebook': {
                'description': "A book of important legal cases.",
                'required': False,
                'usage': "Contains legal precedents"
            }
        }
    },
    'Education Building': {
        'DESCRIPTION': "You are in the Education Building, dedicated to teacher education and research.",
        'EXITS': {'north': 'University Entrance'},
        'ITEMS': ['teaching_plan'],
        'SPECIAL': {
            'teaching_plan': {
                'description': "A detailed teaching lesson plan.",
                'required': False,
                'usage': "Guides teaching activities"
            }
        }
    },
    'Sydney Nanoscience Hub': {
        'DESCRIPTION': "You are in the Sydney Nanoscience Hub, a state-of-the-art research facility.",
        'EXITS': {'south': 'University Entrance'},
        'ITEMS': ['research_proposal'],
        'SPECIAL': {
            'research_proposal': {
                'description': "A nanotechnology research proposal.",
                'required': False,
                'usage': "Outlines research objectives"
            }
        }
    }
}

class HintSystem:
    def __init__(self):
        self.hints = {
            1: "Some say a torn note still clings to the corner of the old sandstone wall in the Quadrangle — as if waiting to be read.",
            2: "Among shelves older than memory, what's forgotten may yet be found.",
            3: "They say a student left some notes on a quiet desk in the Fisher Library... still waiting."
        }
        self.current_hint = 1
        self.mysterious_note_used = 0

    def get_hint(self):
        return self.hints[self.current_hint]

    def advance_hint(self):
        if self.current_hint < len(self.hints):
            self.current_hint += 1
            return True
        return False

class GameStateManager:
    """Manages the game state and player progress"""
    def __init__(self):
        self.player_location = 'University Entrance'
        self.player_inventory = []
        self.game_start_time = None
        self.time_limit = 0
        self.remaining_hints = 0
        self.difficulty = 'normal'
        self.required_items = []
        self.visited_locations = set()
        self.game_score = 0
        self.achievements = set()
        self.puzzle_solved = False
        self.steps_taken = 0
        self.items_collected = 0
        self.start_time = None
        self.end_time = None
        self.special_events = set()
        self.quest_progress = {}
        self.hint_system = HintSystem()
        self.has_entered_campus = False

    def to_dict(self):
        """Convert game state to dictionary for saving"""
        return {
            'player_location': self.player_location,
            'player_inventory': self.player_inventory,
            'game_start_time': self.game_start_time,
            'time_limit': self.time_limit,
            'remaining_hints': self.remaining_hints,
            'difficulty': self.difficulty,
            'required_items': self.required_items,
            'visited_locations': list(self.visited_locations),
            'game_score': self.game_score,
            'achievements': [a.value for a in self.achievements],
            'puzzle_solved': self.puzzle_solved,
            'steps_taken': self.steps_taken,
            'items_collected': self.items_collected,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'special_events': list(self.special_events),
            'quest_progress': self.quest_progress,
            'hint_system': {
                'current_hint': self.hint_system.current_hint,
                'mysterious_note_used': self.hint_system.mysterious_note_used
            },
            'has_entered_campus': self.has_entered_campus
        }

    @classmethod
    def from_dict(cls, data):
        """Create game state from dictionary when loading"""
        state = cls()
        state.player_location = data['player_location']
        state.player_inventory = data['player_inventory']
        state.game_start_time = data['game_start_time']
        state.time_limit = data['time_limit']
        state.remaining_hints = data['remaining_hints']
        state.difficulty = data['difficulty']
        state.required_items = data['required_items']
        state.visited_locations = set(data['visited_locations'])
        state.game_score = data['game_score']
        state.achievements = set(AchievementType(a) for a in data['achievements'])
        state.puzzle_solved = data['puzzle_solved']
        state.steps_taken = data['steps_taken']
        state.items_collected = data['items_collected']
        state.start_time = data['start_time']
        state.end_time = data['end_time']
        state.special_events = set(data['special_events'])
        state.quest_progress = data['quest_progress']
        state.hint_system.current_hint = data['hint_system']['current_hint']
        state.hint_system.mysterious_note_used = data['hint_system']['mysterious_note_used']
        state.has_entered_campus = data['has_entered_campus']
        return state

    def add_achievement(self, achievement_type):
        """Add an achievement and update score"""
        if achievement_type not in self.achievements:
            self.achievements.add(achievement_type)
            self.game_score += 100  # Achievement bonus

    def check_achievements(self):
        """Check and award achievements based on current progress"""
        # Check for visiting all locations
        if len(self.visited_locations) == len(map_data):
            self.add_achievement(AchievementType.VISITED_ALL_LOCATIONS)

        # Check for collecting all items
        total_items = sum(len(location['ITEMS']) for location in map_data.values())
        if self.items_collected == total_items:
            self.add_achievement(AchievementType.COLLECTED_ALL_ITEMS)

        # Check for completing under time limit
        if self.time_limit > 0 and self.end_time:
            time_taken = self.end_time - self.start_time
            if time_taken < self.time_limit:
                self.add_achievement(AchievementType.COMPLETED_UNDER_TIME)

        # Check for not using hints
        if self.remaining_hints == DIFFICULTY_LEVELS[self.difficulty]['hints']:
            self.add_achievement(AchievementType.NO_HINTS_USED)

    def check_access(self, location):
        """Check if player has required items to access a location"""
        if 'ACCESS_CONTROL' in map_data[location]:
            required = map_data[location]['ACCESS_CONTROL']['required_items']
            for item in required:
                if item not in self.player_inventory:
                    print(map_data[location]['ACCESS_CONTROL']['denied_message'])
                    return False
        return True

    def trigger_special_event(self, event_type, item=None):
        """Handle special events and achievements"""
        if event_type == 'engineering_master':
            if all(item in self.player_inventory for item in ['mechanical_tools', 'circuit_board', 'engineering_drawing']):
                self.add_achievement(AchievementType.ENGINEERING_MASTER)
                print("\nCongratulations! You've earned the 'Engineering Master' achievement!")
                return True
        elif event_type == 'teaching_pioneer':
            if 'teaching_plan' in self.player_inventory and self.player_location == 'Education Building':
                self.add_achievement(AchievementType.TEACHING_PIONEER)
                print("\nYou've successfully conducted a class! Achievement unlocked: Teaching Pioneer!")
                return True
        elif event_type == 'nobel_potential':
            if 'microscope_slides' in self.player_inventory and self.player_location == 'Madsen Building':
                self.add_achievement(AchievementType.NOBEL_POTENTIAL)
                print("\nYou've discovered something extraordinary! Achievement unlocked: Nobel Potential!")
                return True
        elif event_type == 'social_butterfly':
            if 'graduation_gown' in self.player_inventory:
                self.add_achievement(AchievementType.SOCIAL_BUTTERFLY)
                print("\nYou've become the center of attention! Achievement unlocked: Social Butterfly!")
                return True
        return False

class GameCommands:
    """Handles all game commands and their execution"""
    def __init__(self, game_state):
        self.state = game_state
        self.commands = {
            'go': self.go,
            'look': self.look,
            'take': self.take,
            'inventory': self.inventory,
            'quit': self.quit,
            'help': self.help,
            'save': self.save,
            'load': self.load,
            'hint': self.hint,
            'use': self.use,
            'examine': self.examine,
            'score': self.score,
            'achievements': self.achievements,
            'stats': self.stats,
            'time': self.time,
            'difficulty': self.difficulty,
            'map': self.show_map
        }

    def process(self, command_input):
        """Process player input and execute corresponding command"""
        normalized_command = command_input.lower()
        words = normalized_command.split()
        
        if not words:
            print("Please enter a command.")
            return GameState.CONTINUE
        
        verb = words[0]
        if verb in self.commands:
            return self.commands[verb](words[1:] if len(words) > 1 else [])
        else:
            print(f"I don't understand '{command_input}'. Type 'help' for available commands.")
            return GameState.CONTINUE

    def go(self, args):
        """Handle movement between locations"""
        if not args:
            print("Where to? (e.g., go north)")
            return GameState.CONTINUE
        
        direction = args[0]
        current_exits = map_data[self.state.player_location]['EXITS']
        
        if direction in current_exits:
            next_location = current_exits[direction]
            if self.state.check_access(next_location):
                self.state.player_location = next_location
                self.state.visited_locations.add(next_location)
                self.state.game_score += 10
                self.state.steps_taken += 1
                display_location(self.state.player_location)
            else:
                return GameState.ACCESS_DENIED
        else:
            print("You can't go that way.")
        return GameState.CONTINUE

    def look(self, args):
        """Display current location information"""
        display_location(self.state.player_location)
        return GameState.CONTINUE

    def take(self, args):
        """Handle item collection"""
        if not args:
            print("Take what? (e.g., take notes)")
            return GameState.CONTINUE
        
        item_name_input = " ".join(args).replace('_', ' ').lower()
        items_here = map_data[self.state.player_location]['ITEMS']
        
        matched_item = None
        for item in items_here:
            if item.lower().replace('_', ' ') == item_name_input:
                matched_item = item
                break
        
        if matched_item:
            items_here.remove(matched_item)
            self.state.player_inventory.append(matched_item)
            print(f"You picked up [{matched_item}].")
            self.state.game_score += 20
            self.state.items_collected += 1
            
            if matched_item == 'COMP9001 notes':
                print("\nCongratulations! You found the lost COMP9001 notes! You win!")
                self.state.add_achievement(AchievementType.FOUND_NOTES)
                self.state.end_time = time.time()
                return GameState.WIN
        else:
            print(f"There is no [{item_name_input}] here.")
        return GameState.CONTINUE

    def inventory(self, args):
        """Display player's inventory"""
        if not self.state.player_inventory:
            print("Your inventory is empty.")
        else:
            print("Your inventory contains: " + ", ".join(self.state.player_inventory))
        return GameState.CONTINUE

    def quit(self, args):
        """Handle game exit"""
        print("Goodbye!")
        return GameState.QUIT

    def help(self, args):
        """Display help information"""
        print("\nAvailable commands:")
        print("  go [direction] - Move in specified direction")
        print("  look - View current location")
        print("  take [item] - Pick up an item")
        print("  inventory - View inventory")
        print("  examine [item] - Examine an item")
        print("  use [item] - Use an item")
        print("  save - Save game")
        print("  load - Load game")
        print("  hint - Get a hint")
        print("  score - View score")
        print("  achievements - View earned achievements")
        print("  stats - View game statistics")
        print("  time - View remaining time")
        print("  difficulty [easy/normal/hard] - Set game difficulty")
        print("  quit - Quit game")
        
        print("\nGame difficulty levels:")
        print("  easy - No time limit, 3 hints available")
        print("  normal - 10 minutes time limit, 2 hints available")
        print("  hard - 5 minutes time limit, 1 hint available")
        
        print("\nAchievements:")
        print("  Entered Campus - First time entering the university")
        print("  Entered Library - First time entering the library")
        print("  Found Notes - Found the lost COMP9001 notes")
        print("  Collected All Items - Collected all available items")
        print("  Visited All Locations - Explored all campus locations")
        print("  Completed Under Time - Finished the game within time limit")
        print("  No Hints Used - Completed the game without using hints")
        print("  Explored Quad - Thoroughly explored the Quadrangle")
        print("  Visited Museum - Explored the Chau Chak Wing Museum")
        print("  Attended Lecture - Attended a lecture in a teaching building")
        return GameState.CONTINUE

    def difficulty(self, args):
        """Set game difficulty level"""
        if not args:
            print(f"\nCurrent difficulty: {self.state.difficulty}")
            print("Available difficulties:")
            for level, details in DIFFICULTY_LEVELS.items():
                time_limit = "No limit" if details['time_limit'] == 0 else f"{details['time_limit']//60} minutes"
                print(f"  {level} - {time_limit} time limit, {details['hints']} hints available")
            return GameState.CONTINUE
        
        new_difficulty = args[0].lower()
        if new_difficulty in DIFFICULTY_LEVELS:
            self.state.difficulty = new_difficulty
            self.state.time_limit = DIFFICULTY_LEVELS[new_difficulty]['time_limit']
            self.state.remaining_hints = DIFFICULTY_LEVELS[new_difficulty]['hints']
            print(f"\nDifficulty set to {new_difficulty}")
            if self.state.time_limit > 0:
                print(f"Time limit: {self.state.time_limit//60} minutes")
            print(f"Available hints: {self.state.remaining_hints}")
        else:
            print("Invalid difficulty level. Use 'easy', 'normal', or 'hard'")
        return GameState.CONTINUE

    def save(self, args):
        """Save game state to file"""
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.state.to_dict(), f)
            print("Game saved successfully.")
        except Exception as e:
            print(f"Error saving game: {e}")
        return GameState.CONTINUE

    def load(self, args):
        """Load game state from file"""
        import json
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print("Error loading game: Save file is corrupted or incomplete. Please delete or reset your save file and try again.")
                        return GameState.CONTINUE
                self.state = GameStateManager.from_dict(data)
                print("Game loaded successfully.")
                display_location(self.state.player_location)
            else:
                print("No saved game found.")
        except Exception as e:
            print(f"Error loading game: {e}")
        return GameState.CONTINUE

    def hint(self, args):
        """Provide game hints"""
        if self.state.remaining_hints > 0:
            self.state.remaining_hints -= 1
            print(f"\nHint: {self.state.hint_system.get_hint()}")
            self.state.game_score -= 50
        else:
            print("You have used all your hints.")
        return GameState.CONTINUE

    def use(self, args):
        """Handle item usage"""
        if not args:
            print("Use what? (e.g., use student_card)")
            return GameState.CONTINUE
        
        item_name = args[0]
        if item_name not in self.state.player_inventory:
            print(f"You don't have [{item_name}] in your inventory.")
            return GameState.CONTINUE
        
        if item_name == 'student_card':
            if not self.state.has_entered_campus:
                print("\nYou show your student card to the security guard.")
                print("The guard examines it carefully and nods.")
                print("'Welcome to the University of Sydney,' they say, stepping aside.")
                self.state.has_entered_campus = True
                self.state.add_achievement(AchievementType.ENTERED_CAMPUS)
                return GameState.SPECIAL_EVENT
            else:
                print("You've already used your student card to enter the campus.")
            return GameState.CONTINUE
        elif item_name == 'mysterious_note':
            self.state.hint_system.mysterious_note_used += 1
            if self.state.hint_system.mysterious_note_used == 1:
                print("\nYou carefully unfold the mysterious note. It reads:")
                print(f"\"{self.state.hint_system.hints[2]}\"")
                print("The note seems to have more to reveal...")
            elif self.state.hint_system.mysterious_note_used == 2:
                print("\nYou examine the mysterious note again. More text appears:")
                print(f"\"{self.state.hint_system.hints[3]}\"")
                print("The note crumbles to dust in your hands.")
                self.state.player_inventory.remove('mysterious_note')
            return GameState.HINT_ACTIVATED
        elif item_name == 'cafeteria_menu':
            print("\nToday's Menu:")
            print("  - Chicken Parma: $12.50")
            print("  - Beef Burger: $10.00")
            print("  - Vegetarian Pizza: $11.00")
            print("  - Daily Special: $9.50")
            return GameState.CONTINUE
        elif item_name == 'graduation_gown':
            if self.state.trigger_special_event('social_butterfly'):
                return GameState.SPECIAL_EVENT
        elif item_name == 'teaching_plan':
            if self.state.trigger_special_event('teaching_pioneer'):
                return GameState.SPECIAL_EVENT
        elif item_name == 'microscope_slides':
            if self.state.trigger_special_event('nobel_potential'):
                return GameState.SPECIAL_EVENT
        
        # Check for engineering master achievement
        if self.state.trigger_special_event('engineering_master'):
            return GameState.SPECIAL_EVENT
        
        print(f"You don't know how to use [{item_name}] here.")
        return GameState.CONTINUE

    def examine(self, args):
        """Examine items in detail"""
        if not args:
            print("Examine what? (e.g., examine student_card)")
            return GameState.CONTINUE
        
        item_name = args[0]
        if item_name in self.state.player_inventory:
            if item_name in map_data[self.state.player_location].get('SPECIAL', {}):
                print(map_data[self.state.player_location]['SPECIAL'][item_name]['description'])
            else:
                print(f"You examine [{item_name}] but find nothing special.")
        else:
            print(f"You don't have [{item_name}] in your inventory.")
        return GameState.CONTINUE

    def score(self, args):
        """Display current score"""
        print(f"\nCurrent score: {self.state.game_score}")
        return GameState.CONTINUE

    def achievements(self, args):
        """Display earned achievements"""
        if not self.state.achievements:
            print("You haven't earned any achievements yet.")
        else:
            print("\nEarned achievements:")
            for achievement in self.state.achievements:
                print(f"  - {achievement.value}")
        return GameState.CONTINUE

    def stats(self, args):
        """Display game statistics"""
        print("\nGame Statistics:")
        print(f"Steps taken: {self.state.steps_taken}")
        print(f"Items collected: {self.state.items_collected}")
        print(f"Locations visited: {len(self.state.visited_locations)}")
        print(f"Time played: {int(time.time() - self.state.start_time)} seconds")
        return GameState.CONTINUE

    def time(self, args):
        """Display remaining time"""
        if self.state.time_limit > 0:
            elapsed = time.time() - self.state.start_time
            remaining = self.state.time_limit - elapsed
            if remaining > 0:
                print(f"\nTime remaining: {int(remaining)} seconds")
            else:
                print("\nTime's up!")
        else:
            print("\nNo time limit in current difficulty.")
        return GameState.CONTINUE

    def show_map(self, args):
        """Display the campus map as a 2D grid based on N/S/E/W relationships, including all locations."""
        ensure_all_locations_connected()  # Always update connections before showing the map
        if 'campus_map' not in self.state.player_inventory:
            print("You need a campus map to view the map.")
            return GameState.CONTINUE

        print("\nGenerating campus map...")

        dir_delta = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }

        from collections import deque, defaultdict
        coords = {}
        start_location_for_map = 'University Entrance'
        if start_location_for_map not in map_data:
            print("Error: Start point 'University Entrance' not found in map data.")
            return GameState.CONTINUE

        queue_bfs = deque([start_location_for_map])
        processed_for_bfs = {start_location_for_map}
        coords[start_location_for_map] = (0, 0)

        while queue_bfs:
            current_loc_name = queue_bfs.popleft()
            current_x, current_y = coords[current_loc_name]
            if current_loc_name not in map_data:
                continue
            for direction, destination_loc_name in map_data[current_loc_name].get('EXITS', {}).items():
                if direction in dir_delta:
                    dx, dy = dir_delta[direction]
                    next_x, next_y = current_x + dx, current_y + dy
                    if destination_loc_name not in processed_for_bfs:
                        if destination_loc_name not in coords:
                            coords[destination_loc_name] = (next_x, next_y)
                        processed_for_bfs.add(destination_loc_name)
                        queue_bfs.append(destination_loc_name)
                    elif destination_loc_name not in coords:
                        coords[destination_loc_name] = (next_x, next_y)

        # Add all unconnected locations to a special row
        all_locations = set(map_data.keys())
        connected_locations = set(coords.keys())
        unconnected_locations = all_locations - connected_locations

        rev_coords = defaultdict(list)
        for loc_name, (x, y) in coords.items():
            rev_coords[(x, y)].append(loc_name)

        if rev_coords:
            all_x_coords = [x for x, y in rev_coords.keys()]
            all_y_coords = [y for x, y in rev_coords.keys()]
            min_x, max_x = min(all_x_coords), max(all_x_coords)
            min_y, max_y = min(all_y_coords), max(all_y_coords)
            grid_height = max_y - min_y + 1
            grid_width = max_x - min_x + 1
            cell_width = 20
            empty_cell_placeholder = " " * cell_width
            grid_display = [[empty_cell_placeholder for _ in range(grid_width)] for _ in range(grid_height)]
            for (x, y), loc_name_list in rev_coords.items():
                grid_y_idx = y - min_y
                grid_x_idx = x - min_x
                raw_label = "/".join(loc_name_list)
                player_marker = ""
                if self.state.player_location in loc_name_list:
                    player_marker = " (*)"
                available_label_width = cell_width - 2 - len(player_marker)
                if len(raw_label) > available_label_width:
                    display_label = raw_label[:available_label_width-3] + "..."
                else:
                    display_label = raw_label
                formatted_label = f"[{display_label.ljust(available_label_width)}{player_marker}]"
                grid_display[grid_y_idx][grid_x_idx] = formatted_label
            print("\nCampus Map (N↑ S↓ E→ W←):")
            print("(*) indicates your current location")
            for row in grid_display:
                print("".join(row))
        else:
            print("No connected locations to display.")

        # Show unconnected locations in a separate row
        if unconnected_locations:
            print("\nUnconnected locations (not reachable from the main map):")
            cell_width = 20
            row = ""
            for loc in sorted(unconnected_locations):
                marker = " (*)" if self.state.player_location == loc else ""
                available_label_width = cell_width - 2 - len(marker)
                label = loc[:available_label_width]
                formatted_label = f"[{label.ljust(available_label_width)}{marker}]"
                row += formatted_label
            print(row)
        return GameState.CONTINUE

def display_location(location_name):
    """Display current location information"""
    current_place = map_data[location_name]
    
    print("\n" + "=" * 50)
    print(current_place['DESCRIPTION'])
    print("=" * 50)
    
    if current_place['ITEMS']:
        print("\nYou see: " + ", ".join(current_place['ITEMS']))
    else:
        print("\nThere are no items of interest here.")
    
    exits = current_place['EXITS']
    available_directions = list(exits.keys())
    print("\nYou can go: " + ", ".join(available_directions))

def display_welcome_screen():
    """Display the game's welcome screen and difficulty selection"""
    print("\n" + "=" * 50)
    print("Welcome to Campus Treasure Hunt!")
    print("A text-based adventure game at the University of Sydney")
    print("=" * 50)
    print("\nYour goal is to find the lost COMP9001 notes somewhere on campus.")
    print("\nAvailable difficulty levels:")
    for level, details in DIFFICULTY_LEVELS.items():
        time_limit = "No limit" if details['time_limit'] == 0 else f"{details['time_limit']//60} minutes"
        print(f"\n{level.capitalize()}:")
        print(f"  - Time limit: {time_limit}")
        print(f"  - Available hints: {details['hints']}")
        print(f"  - Score multiplier: {details['score_multiplier']}x")
    
    while True:
        print("\nSelect difficulty (easy/normal/hard) or type 'help' for more information:")
        choice = input("> ").lower().strip()
        
        if choice in DIFFICULTY_LEVELS:
            return choice
        elif choice == 'help':
            print("\nDifficulty levels explained:")
            print("Easy: Perfect for beginners - no time pressure, plenty of hints")
            print("Normal: Balanced challenge - moderate time limit, limited hints")
            print("Hard: For experienced players - strict time limit, very few hints")
        else:
            print("Invalid choice. Please select 'easy', 'normal', or 'hard'.")

def initialize_game():
    """Initialize game state"""
    # Display welcome screen and get difficulty choice
    difficulty = display_welcome_screen()
    
    # Initialize game state
    state = GameStateManager()
    state.difficulty = difficulty
    state.start_time = time.time()
    state.time_limit = DIFFICULTY_LEVELS[difficulty]['time_limit']
    state.remaining_hints = DIFFICULTY_LEVELS[difficulty]['hints']
    
    # Collect required items
    for location in map_data.values():
        if 'SPECIAL' in location:
            for item, details in location['SPECIAL'].items():
                if details['required']:
                    state.required_items.append(item)
    
    return state

def game_loop():
    """Main game loop"""
    state = initialize_game()
    commands = GameCommands(state)
    
    print("\n" + "=" * 50)
    print(f"Starting game in {state.difficulty} mode")
    if state.time_limit > 0:
        print(f"Time limit: {state.time_limit//60} minutes")
    print(f"Available hints: {state.remaining_hints}")
    print("\nType 'help' for available commands.")
    print("Type 'difficulty' to view or change difficulty settings.")
    print("=" * 50)
    
    # Initial game state check
    if not state.has_entered_campus:
        print("\nYou are at the university entrance. You need to show your student card to enter.")
    
    display_location(state.player_location)
    
    game_status = GameState.CONTINUE
    while game_status == GameState.CONTINUE:
        if state.time_limit > 0:
            elapsed_time = time.time() - state.start_time
            if elapsed_time > state.time_limit:
                print("\nTime's up! Game over.")
                return
        
        command = input("\n> ")
        game_status = commands.process(command)
        
        # Check achievements after each command
        state.check_achievements()
        
        # Handle special events
        if game_status == GameState.SPECIAL_EVENT:
            game_status = GameState.CONTINUE
        elif game_status == GameState.ACCESS_DENIED:
            game_status = GameState.CONTINUE
    
    print(f"\nGame over. Final score: {state.game_score}")
    if state.achievements:
        print("\nAchievements earned:")
        for achievement in state.achievements:
            print(f"  - {achievement.value}")

def ensure_all_locations_connected():
    """Ensure all locations in map_data are connected from 'University Entrance', using only N/S/E/W directions."""
    from collections import deque
    directions = ['north', 'south', 'east', 'west']
    reverse_dir = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
    # Step 1: Find all reachable locations
    reachable = set()
    queue = deque(['University Entrance'])
    while queue:
        loc = queue.popleft()
        if loc in reachable:
            continue
        reachable.add(loc)
        for dest in map_data[loc]['EXITS'].values():
            if dest not in reachable:
                queue.append(dest)
    # Step 2: Find all locations in map_data
    all_locations = set(map_data.keys())
    unreachable = all_locations - reachable
    # Step 3: For each unreachable location, connect it to a connected node with a free N/S/E/W direction
    for unloc in unreachable:
        for node in list(reachable):
            used_dirs = set(map_data[node]['EXITS'].keys())
            available_dirs = [d for d in directions if d not in used_dirs]
            if available_dirs:
                dir = available_dirs[0]
                map_data[node]['EXITS'][dir] = unloc
                if 'EXITS' not in map_data[unloc]:
                    map_data[unloc]['EXITS'] = {}
                map_data[unloc]['EXITS'][reverse_dir[dir]] = node
                reachable.add(unloc)
                break

# Call this function at the start of the game
ensure_all_locations_connected()

if __name__ == "__main__":
    game_loop() 