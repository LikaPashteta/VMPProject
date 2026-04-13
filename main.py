import streamlit as st
import time
import json
import os
import random
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from streamlit_autorefresh import st_autorefresh

SAVE_FILE = "savegame.json"
STORY_FILE = "story.json"
RECOVERY_RATE_HP = 600
RECOVERY_RATE_ENERGY = 600
HP_PER_LEVEL = 5
ENERGY_PER_LEVEL = 3

def load_story() -> Dict[str, Any]:
    try:
        with open(STORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки сюжета: {e}")
        return {
            "locations": {
                "Таверна «Красочный переполох»": {
                    "actions": [
                        {"description": "Выпивает сидр", "energy_cost": 2, "items": []}
                    ]
                }
            },
            "possible_locations": ["Таверна «Красочный переполох»"],
            "default_actions": ["Ничего интересного не происходит."]
        }

story_data = load_story()

@dataclass
class Character:
    name: str = ""
    race: str = ""
    backstory: str = ""
    level: int = 1
    hp: int = 100
    max_hp: int = 100
    energy: int = 50
    max_energy: int = 50
    location: str = "Таверна «Красочный переполох»"
    last_update: float = 0.0
    inventory: Dict[str, int] = field(default_factory=dict)
    last_action_time: float = 0.0
    action_interval: int = 1
    history: List[Dict[str, Any]] = field(default_factory=list)
    actions_in_current_location: int = 0
    total_actions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['inventory'] = [{"name": k, "count": v} for k, v in self.inventory.items()]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        inv_list = data.get('inventory', [])
        inventory = {}
        for item in inv_list:
            inventory[item['name']] = item['count']
        data['inventory'] = inventory
        if 'actions_in_current_location' not in data:
            data['actions_in_current_location'] = 0
        if 'total_actions' not in data: 
            data['total_actions'] = 0
        return cls(**data)

RACES = {
    "Человек": {
        "hp_bonus": 0,
        "energy_bonus": 0,
        "description": "Универсальная раса, приспособленная к любым условиям."
    },
    "Эльф": {
        "hp_bonus": -10,
        "energy_bonus": 10,
        "description": "Древний народ с острым слухом и природной ловкостью."
    },
    "Дварф": {
        "hp_bonus": 15,
        "energy_bonus": -5,
        "description": "Крепкие подземные жители, мастера кузнечного дела."
    },
    "Полурослик": {
        "hp_bonus": -5,
        "energy_bonus": 15,
        "description": "Хитрые и энергичные, но не слишком выносливые."
    }
}

BACKSTORIES = [
    "Вас родители продали цыганям.",
    "Вы беглец из страны, в которой за вашу голову назначена награда.",
    "Вы потеряли память после удара молнии во время шторма.",
    "Вы изгнаны из родной деревни за преступление, которого не совершали.",
    "Вы — последний выживший ученик уничтоженной художественной школы.",
    "Ваш наставник погиб, оставив вам загадочную палитру.",
    "Вы бежали из деревни, спасаясь от болезни."
]

def generate_backstory() -> str:
    return random.choice(BACKSTORIES)

def save_game(char: Character) -> bool:
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(char.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Ошибка сохранения: {e}")
        return False

def load_game() -> Optional[Character]:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Character.from_dict(data)
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return None

def apply_recovery(char: Character):
    if char.last_update == 0.0:
        char.last_update = time.time()
        return
    now = time.time()
    elapsed_hours = (now - char.last_update) / 3600.0
    if elapsed_hours > 0:
        hp_recovered = int(elapsed_hours * RECOVERY_RATE_HP)
        energy_recovered = int(elapsed_hours * RECOVERY_RATE_ENERGY)
        char.hp = min(char.max_hp, char.hp + hp_recovered)
        char.energy = min(char.max_energy, char.energy + energy_recovered)
        char.last_update = now

def generate_action_message(char: Character, story: Dict[str, Any]) -> str:
    loc = char.location
    location_data = story.get("locations", {}).get(loc, {})
    actions = location_data.get("actions", [])

    if actions:
        action = random.choice(actions)
        description = action["description"]
        cost = action.get("energy_cost", 0)
        char.energy = max(0, char.energy - cost)
        hp_change = action.get("hp_change", 0)
        char.hp = max(0, min(char.max_hp, char.hp + hp_change))
        items_list = action.get("items", [])
        item_text = ""
        if items_list and random.random() < 0.7:
            item = random.choice(items_list)
            char.inventory[item] = char.inventory.get(item, 0) + 1
            item_text = f" Найдено: {item}."
        return f"{description}.{item_text}"
    else:
        default_actions = story.get("default_actions", ["Ничего не произошло."])
        return random.choice(default_actions)

def maybe_change_location(char: Character, story: Dict[str, Any]):
    char.actions_in_current_location += 1
    threshold = random.randint(3, 5)
    if char.actions_in_current_location >= threshold:
        possible_locations = story.get("possible_locations", [])
        if possible_locations:
            other_locations = [loc for loc in possible_locations if loc != char.location]
            if other_locations:
                new_loc = random.choice(other_locations)
                char.location = new_loc
                char.actions_in_current_location = 0
                timestamp = datetime.now().strftime("%H:%M:%S")
                char.history.append({"time": timestamp, "text": f"🚪 Герой переместился в локацию: {new_loc}."})
                if len(char.history) > 10:
                    char.history.pop(0)

def check_level_up(char: Character):
    new_level = (char.total_actions // 10) + 1
    if new_level > 100:
        new_level = 100
    if new_level > char.level:
        old_level = char.level
        char.level = new_level
        char.max_hp += HP_PER_LEVEL * (new_level - old_level)
        char.max_energy += ENERGY_PER_LEVEL * (new_level - old_level)
        char.hp = char.max_hp
        char.energy = char.max_energy
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"🎉 Уровень повышен! Теперь {char.level} уровень. Максимальное здоровье +{HP_PER_LEVEL*(new_level-old_level)}, энергия +{ENERGY_PER_LEVEL*(new_level-old_level)}."
        char.history.append({"time": timestamp, "text": msg})
        if len(char.history) > 10:
            char.history.pop(0)

def try_add_action(char: Character):
    if char.last_action_time == 0.0:
        char.last_action_time = time.time()
        return

    now = time.time()
    elapsed_minutes = (now - char.last_action_time) / 60.0
    if elapsed_minutes >= char.action_interval:
        msg = generate_action_message(char, story_data)
        timestamp = datetime.now().strftime("%H:%M:%S")
        char.history.append({"time": timestamp, "text": msg})
        if len(char.history) > 10:
            char.history.pop(0)
        char.last_action_time = now
        char.total_actions += 1
        check_level_up(char)

        maybe_change_location(char, story_data)

def create_character_screen():
    st.title("Создание героя")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        name = st.text_input("Введите имя персонажа", max_chars=20, placeholder="Напр.: Марсиль")
        race_options = list(RACES.keys())
        selected_race = st.selectbox("Выберите расу", race_options)
        st.caption(RACES[selected_race]["description"])

        st.subheader("Предыстория")
        backstory_option = st.radio(
            "Выберите способ определения предыстории:",
            ["Сгенерировать случайную", "Выбрать из списка", "Написать свою"]
        )

        if backstory_option == "Сгенерировать случайную":
            if "temp_backstory" not in st.session_state:
                st.session_state.temp_backstory = generate_backstory()
            if st.button("🎲 Сгенерировать новую"):
                st.session_state.temp_backstory = generate_backstory()
            backstory = st.session_state.temp_backstory
            st.info(backstory)
        elif backstory_option == "Выбрать из списка":
            backstory = st.selectbox("Выберите предысторию", BACKSTORIES)
        else:
            backstory = st.text_area("Напишите свою предысторию", height=100,
                                     placeholder="Расскажите, кем был ваш герой...")

    with col2:
        st.subheader("Характеристики")
        race_bonus = RACES[selected_race]
        base_hp = 100 + race_bonus["hp_bonus"]
        base_energy = 50 + race_bonus["energy_bonus"]
        st.metric("Базовое здоровье", base_hp)
        st.metric("Базовая энергия", base_energy)
        if selected_race != "Человек":
            st.caption(f"Модификаторы расы: {race_bonus['hp_bonus']:+d} / {race_bonus['energy_bonus']:+d}")

    st.markdown("---")
    if st.button("🎮 Начать игру", type="primary", disabled=not name):
        new_char = Character(
            name=name,
            race=selected_race,
            backstory=backstory,
            hp=base_hp,
            max_hp=base_hp,
            energy=base_energy,
            max_energy=base_energy,
            location="Таверна «Красочный переполох»",
            last_update=time.time(),
            inventory={},
            last_action_time=time.time(),
            action_interval=1,
            history=[],
            actions_in_current_location=0,
            total_actions=0             
        )
        st.session_state.char = new_char
        save_game(new_char)
        st.session_state.character_created = True
        st.rerun()

def main_game():
    char = st.session_state.char
    apply_recovery(char)
    try_add_action(char)
    save_game(char)

    st.title(f"🎨 Приключение {char.name}")

    with st.sidebar:
        st.header(f"{char.name}")
        st.caption(f"Раса: {char.race}")
        st.metric("Уровень", char.level)
        st.progress(char.hp / char.max_hp, f"Здоровье: {char.hp}/{char.max_hp}")
        st.progress(char.energy / char.max_energy, f"Энергия: {char.energy}/{char.max_energy}")
        st.caption(f"📍 Местоположение: {char.location}")

        with st.expander("Предыстория"):
            st.write(char.backstory)

        with st.expander("Инвентарь"):
            if char.inventory:
                for item, count in char.inventory.items():
                    st.write(f"- {item} x{count}")
            else:
                st.write("Пусто")

        st.subheader("Режим активности")
        interval = st.radio(
            "Отправлять сообщения каждые:",
            options=[1, 3, 5],
            index=[1,3,5].index(char.action_interval) if char.action_interval in [1,3,5] else 0,
            format_func=lambda x: f"{x} мин."
        )
        if interval != char.action_interval:
            char.action_interval = interval
            char.last_action_time = time.time()
            save_game(char)
            st.rerun()

        st.subheader("Судьба героя")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Сделать гадость", disabled=char.energy < 10):
                char.energy -= 10
                timestamp = datetime.now().strftime("%H:%M:%S")
                if random.random() < 0.7:
                    loss = random.randint(10, 40)
                    char.hp = max(0, char.hp - loss)
                    msg = f"Герой нарвался на неприятности и потерял {loss} здоровья."
                else:
                    msg = "Сегодня герой слишком удачлив."
                char.history.append({"time": timestamp, "text": msg})
                if len(char.history) > 10:
                    char.history.pop(0)
                save_game(char)
                st.rerun()
        with col2:
            if st.button("Сделать радость", disabled=char.energy < 10):
                char.energy -= 10
                timestamp = datetime.now().strftime("%H:%M:%S")
                if random.random() < 0.7:
                    gain = random.randint(10, 40)
                    char.hp = min(char.max_hp, char.hp + gain)
                    msg = f"Герой нашёл способ подлечиться и восстановил {gain} здоровья."
                else:
                    loss = random.randint(1, 11)
                    char.hp = max(0, char.hp - loss)
                    msg = f"Сегодня удача покинула героя. Потеряно {loss} здоровья."
                char.history.append({"time": timestamp, "text": msg})
                if len(char.history) > 10:
                    char.history.pop(0)
                save_game(char)
                st.rerun()

        st.subheader("Божественное вмешательство")
        if st.button("Полное восстановление", use_container_width=True):
            char.hp = char.max_hp
            char.energy = char.max_energy
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = "Боги смилостивились — здоровье и энергия полностью восстановлены!"
            char.history.append({"time": timestamp, "text": msg})
            if len(char.history) > 10:
                char.history.pop(0)
            save_game(char)
            st.rerun()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Сохранить"):
                if save_game(char):
                    st.success("Сохранено!")
                else:
                    st.error("Ошибка!")
        with col_btn2:
            if st.button("Сброс"):
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                st.session_state.character_created = False
                st.rerun()

    st.subheader("Текущая активность")
    st.info(f"Герой занимается делами каждые **{char.action_interval} мин.** (Всего действий: {char.total_actions})")

    st.subheader("Журнал событий (последние 10)")
    if not char.history:
        st.write("Пока ничего не произошло.")
    else:
        for entry in reversed(char.history):
            st.write(f"`[{entry['time']}]` {entry['text']}")

    if char.energy < 10:
        st.warning("У вас мало энергии. Герой действует медленнее, но восстановление идёт со временем.")

def main():
    st.set_page_config(page_title="Текстовый Godville", page_icon="🎨")
    st_autorefresh(interval=10000, key="autorefresh")

    if "character_created" not in st.session_state:
        loaded_char = load_game()
        if loaded_char:
            st.session_state.char = loaded_char
            apply_recovery(st.session_state.char)
            st.session_state.character_created = True
        else:
            st.session_state.character_created = False

    if not st.session_state.character_created:
        create_character_screen()
    else:
        main_game()

if __name__ == "__main__":
    main()
