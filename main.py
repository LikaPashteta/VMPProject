import streamlit as st
import time
import json
import os
import random
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
SAVES_FILE = "savegames.json"
STORY_FILE = "story.json"
RECOVERY_RATE_HP = 100
RECOVERY_RATE_ENERGY = 100
HP_PER_LEVEL = 5
ENERGY_PER_LEVEL = 3
def load_story() -> Dict[str, Any]:
    try:
        with open(STORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {
            "locations": {
                "Таверна «Красочный переполох»": {
                    "actions": [
                        {"description": "🍺 пьёт эль", "energy_cost": 2, "items": []}
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
        char = cls(**data)
        char.hp = max(0, min(char.hp, char.max_hp))
        char.energy = max(0, min(char.energy, char.max_energy))
        return char
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
def load_all_characters() -> Dict[str, Character]:
    if not os.path.exists(SAVES_FILE):
        return {}
    try:
        with open(SAVES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chars = {}
            for name, char_dict in data.items():
                chars[name] = Character.from_dict(char_dict)
            return chars
    except Exception as e:
        return {}
def save_all_characters(chars: Dict[str, Character]) -> bool:
    try:
        data = {name: char.to_dict() for name, char in chars.items()}
        with open(SAVES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False
def save_current_character(char: Character, all_chars: Dict[str, Character]):
    all_chars[char.name] = char
    save_all_characters(all_chars)
def delete_character(name: str, all_chars: Dict[str, Character]) -> bool:
    if name in all_chars:
        del all_chars[name]
        return save_all_characters(all_chars)
    return False
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
    char.hp = max(0, min(char.hp, char.max_hp))
    char.energy = max(0, min(char.energy, char.max_energy))
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
def create_character_screen(existing_names: List[str] = None):
    col_hero_img, col_hero_txt = st.columns([0.30, 0.9])
    with col_hero_img:
        if os.path.exists("cat-headphones.png"):
            st.image("cat-headphones.png", width=110)
        else:
            st.write("🎮")
    with col_hero_txt:
        st.subheader("Создание героя")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Введите имя персонажа", max_chars=20, placeholder="Напр.: Марсиль")
        if existing_names and name in existing_names:
            st.warning("Персонаж с таким именем уже существует. Выберите другое имя.")
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
            if st.button("Сгенерировать новую"):
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
            st.caption(f"Модификаторы расы: ❤️ {race_bonus['hp_bonus']:+d} / ⚡ {race_bonus['energy_bonus']:+d}")
    st.markdown("---")
    name_ok = name and (existing_names is None or name not in existing_names)
    if st.button("Начать игру", type="primary", disabled=not name_ok):
        new_char = Character(
            name=name,
            race=selected_race,
            backstory=backstory,
            hp=base_hp,
            max_hp=base_hp,
            energy=base_energy,
            max_energy=base_energy,
            location="Таверна «Усталый путник»",
            last_update=time.time(),
            inventory={},
            last_action_time=time.time(),
            action_interval=1,
            history=[],
            actions_in_current_location=0,
            total_actions=0
        )
        all_chars = load_all_characters()
        all_chars[name] = new_char
        if save_all_characters(all_chars):
            st.session_state.char_name = name
            st.session_state.character_created = True
            st.rerun()
        else:
            st.error("Не удалось сохранить персонажа.")
def character_selection_screen():
    col_hero_img, col_hero_txt = st.columns([0.30, 0.9])
    with col_hero_img:
        if os.path.exists("cat-headphones.png"):
            st.image("cat-headphones.png", width=110)
        else:
            st.write("🎮")
    with col_hero_txt:
        st.subheader("Выбор героя")
    all_chars = load_all_characters()
    if all_chars:
        char_names = list(all_chars.keys())
        selected = st.selectbox("Выберите персонажа", char_names)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔️ Играть за выбранного", use_container_width=True):
                st.session_state.char_name = selected
                st.session_state.character_created = True
                st.rerun()
        with col2:
            if st.button("❌ Удалить персонажа", use_container_width=True):
                if delete_character(selected, all_chars):
                    st.success(f"Персонаж {selected} удалён.")
                    if st.session_state.get('char_name') == selected:
                        st.session_state.character_created = False
                        st.session_state.char_name = None
                    st.rerun()
                else:
                    st.error("Ошибка при удалении.")
    else:
        st.info("Нет сохранённых персонажей.")
    st.markdown("---")
    col_pers_img, col_pers_txt = st.columns([0.30, 0.9])
    with col_pers_img:
        if os.path.exists("pers.png"):
            st.image("pers.png", width=110)
        else:
            st.write("🎮")
    with col_pers_txt:
        st.subheader("Или создайте нового персонажа")
    if st.button("Создать нового персонажа", use_container_width=True):
        st.session_state.show_creation = True
        st.rerun()
def main_game():
    all_chars = load_all_characters()
    char_name = st.session_state.char_name
    if char_name not in all_chars:
        st.error("Персонаж не найден. Возврат к выбору.")
        st.session_state.character_created = False
        st.rerun()
    char = all_chars[char_name]
    apply_recovery(char)
    try_add_action(char)
    save_current_character(char, all_chars)
    st.title(f"Путешествие героя {char.name}")
    with st.sidebar:
        col_name_img, col_name_txt = st.columns([0.40, 0.7])
        with col_name_img:
            if os.path.exists("name.png"):
                st.image("name.png", width=90)
            else:
                st.write("😎")
        with col_name_txt:
            st.subheader(f"{char.name}")
        st.caption(f"Раса: {char.race}")
        st.metric("Уровень", char.level)
        hp_progress = max(0.0, min(1.0, char.hp / char.max_hp if char.max_hp > 0 else 0.0))
        energy_progress = max(0.0, min(1.0, char.energy / char.max_energy if char.max_energy > 0 else 0.0))
        col_hp_img, col_hp_bar = st.columns([0.17, 0.90])
        with col_hp_img:
            if os.path.exists("hp.png"):
                st.image("hp.png", width=50)
            else:
                st.write("❤️")
        with col_hp_bar:
            st.progress(hp_progress, f"Здоровье: {char.hp}/{char.max_hp}")
        col_en_img, col_en_bar = st.columns([0.17, 0.90])
        with col_en_img:
            if os.path.exists("energy.png"):
                st.image("energy.png", width=50)
            else:
                st.write("⚡")
        with col_en_bar:
            st.progress(energy_progress, f" Энергия: {char.energy}/{char.max_energy}")
        st.caption(f"📍 Местоположение: {char.location}")
        col_img1, col_txt1 = st.columns([0.3, 0.7])
        with col_img1:
            if os.path.exists("backstory.png"):
                st.image("backstory.png", width=70)
            else:
                st.write("📜")
        with col_txt1:
            st.subheader("Предыстория")
        with st.expander("Читать предысторию"):
            st.write(char.backstory)
        col_img2, col_txt2 = st.columns([0.3, 0.7])
        with col_img2:
            if os.path.exists("inventory.png"):
                st.image("inventory.png", width=70)
            else:
                st.write("🎒")
        with col_txt2:
            st.subheader("Инвентарь")
        with st.expander("Просмотреть инвентарь"):
            if char.inventory:
                for item, count in char.inventory.items():
                    st.write(f"- {item} x{count}")
            else:
                st.write("Пусто")
        st.subheader("Действия")
        col_act_img, col_act_text = st.columns([0.35, 0.90])
        with col_act_img:
            if os.path.exists("mode.png"):
                st.image("mode.png", width=80)
            else:
                st.write("⏱️")
        with col_act_text:
            interval = st.radio(
                "Выберите частоту",
                options=[0.1, 1, 3, 5],
                index=[0.1, 1,3,5].index(char.action_interval) if char.action_interval in [0.1,1,3,5] else 0,
                format_func=lambda x: f"{x} мин."
            )
        if interval != char.action_interval:
            char.action_interval = interval
            char.last_action_time = time.time()
            save_current_character(char, all_chars)
            st.rerun()
        st.subheader("Судьба героя")
        col_evil_img, col_evil_txt = st.columns([0.2, 0.8])
        with col_evil_img:
            if os.path.exists("evil.png"):
                st.image("evil.png", width=60)
            else:
                st.write("👹")
        with col_evil_txt:
            if st.button("Сделать гадость", disabled=char.energy < 10, key="evil"):
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
                save_current_character(char, all_chars)
                st.rerun()
        col_good_img, col_good_txt = st.columns([0.2, 0.8])
        with col_good_img:
            if os.path.exists("good.png"):
                st.image("good.png", width=60)
            else:
                st.write("😇")
        with col_good_txt:
            if st.button("Сделать радость", disabled=char.energy < 10, key="good"):
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
                save_current_character(char, all_chars)
                st.rerun()
        st.subheader("Божественное вмешательство")
        col_heal_img, col_heal_txt = st.columns([0.2, 0.8])
        with col_heal_img:
            if os.path.exists("heal.png"):
                st.image("heal.png", width=60)
            else:
                st.write("💖")
        with col_heal_txt:
            if st.button("Полное восстановление", use_container_width=True, key="heal"):
                char.hp = char.max_hp
                char.energy = char.max_energy
                timestamp = datetime.now().strftime("%H:%M:%S")
                msg = "Боги смилостивились — здоровье и энергия полностью восстановлены!"
                char.history.append({"time": timestamp, "text": msg})
                if len(char.history) > 10:
                    char.history.pop(0)
                save_current_character(char, all_chars)
                st.rerun()
        st.markdown("---")
        col_switch_img, col_switch_btn = st.columns([0.17, 0.70])
        with col_switch_img:
            if os.path.exists("change.png"):
             st.image("change.png", width=50)
            else:
                st.write("🔄")
        with col_switch_btn:
            if st.button("Сменить персонажа", use_container_width=True):
                st.session_state.character_created = False
                st.session_state.show_creation = False
                st.rerun()
    col_img_act, col_txt_act = st.columns([0.17, 0.8])
    with col_img_act:
        if os.path.exists("cat-headphones.png"):
            st.image("cat-headphones.png", width=80)
        else:
            st.write("📢")
    with col_txt_act:
        st.subheader("Текущая активность героя")
    st.info(f"Герой занимается делами каждые **{char.action_interval} мин.** (Всего действий: {char.total_actions})")
    st.subheader("📜 Журнал событий (последние 10)")
    if not char.history:
        st.write("Пока ничего не произошло.")
    else:
        for entry in reversed(char.history):
            st.write(f"`[{entry['time']}]` {entry['text']}")
    if char.energy < 10:
        st.warning("⚠️ У вас мало энергии. Герой останавливается, пока не воссстановится.")
def main():
    st.set_page_config(page_title="Интересности тут", page_icon="icon.png")
    st_autorefresh(interval=10000, key="autorefresh")
    if "character_created" not in st.session_state:
        st.session_state.character_created = False
    if "show_creation" not in st.session_state:
        st.session_state.show_creation = False
    if "char_name" not in st.session_state:
        st.session_state.char_name = None
    if not st.session_state.character_created:
        if st.session_state.show_creation:
            all_chars = load_all_characters()
            existing_names = list(all_chars.keys())
            create_character_screen(existing_names)
            if st.button("Назад к выбору персонажа"):
                st.session_state.show_creation = False
                st.rerun()
        else:
            character_selection_screen()
    else:
        main_game()
if __name__ == "__main__":
    main()
