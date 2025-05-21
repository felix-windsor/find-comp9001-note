# 🎓 find-comp9001-note

*A text-based Python adventure game set on the University of Sydney campus.*

Explore a richly structured virtual campus in search of the **lost COMP9001 notes**. Navigate iconic locations, collect critical items, and unlock achievements while managing your time and resources wisely.

---

## 🕹️ Features

- 🗺️ Explore iconic USYD locations: Quadrangle, Fisher Library, Chau Chak Wing Museum, and more  
- 🔑 Collect items to unlock new areas and trigger special events  
- 🏆 Earn achievements for exploration, puzzle-solving, and speed  
- 💬 Text-based interface with natural language commands  
- ⏱️ Difficulty settings: Easy (no time limit) to Hard (strict time & hints)  
- 💾 Save & Load system to resume your journey anytime  

---

## 🚀 Getting Started

1. Make sure you have Python 3 installed.
2. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/find-comp9001-note.git
    cd find-comp9001-note
    ```

3. Run the game:

    ```bash
    python3 game.py
    ```

---

## 💡 Sample Gameplay

```text
>>> Welcome to Campus Treasure Hunt!
Your goal is to find the lost COMP9001 notes somewhere on campus.

> take student_card
You picked up [student_card].

> use student_card
The guard examines it carefully and nods.
"Welcome to the University of Sydney."

> go north
You are in the Main Quadrangle, the heart of the university...

```


### 📁 Project Structure

> **💡 Tip:** This structure helps understand how the project is modularized.

| File/Module         | Description                                         |
|---------------------|-----------------------------------------------------|
| `game.py`           | Main game loop and command processor                |
| `map_data`          | Location, item, and access control definitions      |
| `GameStateManager`  | Handles inventory, scoring, achievements, etc.      |
| `HintSystem`        | Controls hint logic and item-based reveals          |
| `game_save.json`    | Automatically created for save/load functionality   |

## 📜 License

This project is licensed under the [MIT License](LICENSE).
