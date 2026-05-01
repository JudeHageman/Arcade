"""
dialog_data.py - NPC dialog tree definitions for Island Gardener
Author: Minju Seo
Date:   2026-04-21
"""

from dialog_graph import DialogGraph
from ai_npc import AIHandler

# ---------------------------------------------------------------------------
# NPC 1 — Mayor Poodle (Sparkling Shore)
# ---------------------------------------------------------------------------
def _make_mayor_poodle():
    dg = DialogGraph("Mayor Poodle")

    # Nodes (Branching Tree)
    dg.add_dialog_node("greet", "Welcome to Sparkling Shore! I'm Mayor Poodle. Isn't the ocean breeze lovely?")
    dg.add_dialog_node("mechanics", "As a gardener, you'll need to use your shovel to plant seeds and water them daily.")
    dg.add_dialog_node("lore", "Our island was once a giant floating botanical garden for the ancient gods.")
    dg.add_dialog_node("quest_start", "We need a brave gardener to restore the old plaza. Will you help us?")
    dg.add_dialog_node("farewell", "Wonderful! I'll be here if you need more guidance.", node_type="end")

    # Choices (Branching)
    dg.add_choice("greet", "mechanics", "How do I garden here?")
    dg.add_choice("greet", "lore", "Tell me about the island's history.")
    dg.add_choice("mechanics", "quest_start", "I'm ready to help!")
    dg.add_choice("lore", "quest_start", "That's deep. What can I do?")
    dg.add_choice("quest_start", "farewell", "Count me in!")

    dg.set_start("greet")
    return dg

# ---------------------------------------------------------------------------
# NPC 2 — Archaeologist Turtle (Emerald Jungle)
# ---------------------------------------------------------------------------
def _make_archaeologist_turtle():
    dg = DialogGraph("Archaeologist Turtle")

    # Nodes (AI Wisdom Node)
    dg.add_dialog_node("intro", "Patience... The earth speaks in whispers. What have you brought me?")
    dg.add_dialog_node("identify_ai", "Let me examine this artifact with my ancient knowledge...", node_type="ai")
    dg.add_dialog_node("artifact_lore", "Most of these seeds are centuries old. They require special soil to grow.")
    dg.add_dialog_node("bye", "Slow and steady, young one. The jungle doesn't rush.", node_type="end")

    # Edges
    dg.add_choice("intro", "identify_ai", "Can you identify this ancient seed? (AI Chat)")
    dg.add_choice("intro", "artifact_lore", "Tell me about the jungle's artifacts.")
    dg.add_choice("identify_ai", "intro", "I have another question.")
    dg.add_choice("artifact_lore", "bye", "Thank you, wise one.")
    dg.add_choice("intro", "bye", "Goodbye, Silas.")

    dg.set_start("intro")
    return dg

# ---------------------------------------------------------------------------
# NPC 3 — Postman Seagull (Cloudy Heights)
# ---------------------------------------------------------------------------
def _make_postman_seagull():
    dg = DialogGraph("Postman Seagull")

    # Nodes (Looping Menu for Fast Travel)
    dg.add_dialog_node("menu", "Squawk! Busy day! Mail to deliver, places to go! Where to?")
    dg.add_dialog_node("travel_shore", "Flying you to Sparkling Shore! Hold onto your hat!")
    dg.add_dialog_node("travel_jungle", "To the Emerald Jungle! Watch out for the vines!")
    dg.add_dialog_node("delivery", "I have a package for you! It's... oh wait, I lost it. Just kidding!")
    dg.add_dialog_node("exit", "Fly high! Catch the next draft!", node_type="end")

    # Edges (Looping Menu)
    dg.add_choice("menu", "travel_shore", "Take me to Sparkling Shore.")
    dg.add_choice("menu", "travel_jungle", "Take me to Emerald Jungle.")
    dg.add_choice("menu", "delivery", "Any mail for me?")
    dg.add_choice("menu", "exit", "Just resting, thanks.")

    # Loop back to menu
    dg.add_choice("delivery", "menu", "Wait, I need to go somewhere else.")

    dg.set_start("menu")
    return dg

# ---------------------------------------------------------------------------
# AI Handler (Archaeologist Turtle)
# ---------------------------------------------------------------------------
turtle_ai = AIHandler(
    personality=(
        "You are Archaeologist Turtle, a very old and wise turtle living in the Emerald Jungle. "
        "You speak very slowly and calmly. You are an expert on ancient seeds and history. "
        "You often use the phrase 'Patience is a virtue' and keep replies under 3 sentences."
    )
)

# ---------------------------------------------------------------------------
# NPC_DATA
# ---------------------------------------------------------------------------
NPC_DATA = [
    {
        "name": "Mayor Poodle",
        "grid_x": 30, "grid_y": 20, # Adjust to your Sparkling Shore map coordinates
        "sprite_name": "mayor_poodle",
        "dialog": _make_mayor_poodle(),
        "ai_handler": None,
    },
    {
        "name": "Archaeologist Turtle",
        "grid_x": 40, "grid_y": 10, # Adjust to your Emerald Jungle map coordinates
        "sprite_name": "arch_turtle",
        "dialog": _make_archaeologist_turtle(),
        "ai_handler": turtle_ai,
    },
    {
        "name": "Postman Seagull",
        "grid_x": 12, "grid_y": 10, # Adjust to your Cloudy Heights map coordinates
        "sprite_name": "postman_seagull",
        "dialog": _make_postman_seagull(),
        "ai_handler": None,
    },
]