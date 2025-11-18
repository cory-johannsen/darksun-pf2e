"""
Chapter Five: Monsters of Athas HTML Postprocessing

Handles paragraph breaks in the introductory text that spans multiple 
text blocks in the source PDF, and reconstructs monster manual pages.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic
from tools.pdf_pipeline.postprocessors.chapter_five_monsters_reconstruction import reconstruct_all_monster_pages

logger = logging.getLogger(__name__)


def apply_intro_paragraph_breaks(html: str) -> str:
    """
    Split the intro text into 3 separate paragraphs.
    
    The intro currently appears as a single paragraph but should be split into:
    1. "Life is a mysterious... sun-baked clay."
    2. "To survive... pages that follow."
    3. "Over the course... is often deadly on Athas."
    
    Args:
        html: The HTML content
        
    Returns:
        HTML with proper paragraph breaks
    """
    logger.info("Applying intro paragraph breaks for Chapter Five: Monsters of Athas")
    
    # Find the intro paragraph that starts with "Life is a mysterious"
    # and contains all three parts that need to be split
    intro_pattern = re.compile(
        r'(<p>Life is a mysterious.*?is often deadly on Athas\.</p>)',
        re.DOTALL
    )
    
    match = intro_pattern.search(html)
    if not match:
        logger.warning("⚠️  Could not find intro paragraph to split")
        return html
    
    full_intro = match.group(1)
    
    # Now split at the key break points
    # Break 1: After "sun-baked clay." insert </p><p> before "To survive"
    # Break 2: After "pages that follow." insert </p><p> before "Over the course"
    
    modified = full_intro
    
    # First break: split before "To survive"
    modified = re.sub(
        r'(sun-baked clay\.\s+)(To survive)',
        r'\1</p>\n<p>\2',
        modified
    )
    
    # Second break: split before "Over the course"
    modified = re.sub(
        r'(pages that follow\.\s+)(Over the course)',
        r'\1</p>\n<p>\2',
        modified
    )
    
    if modified != full_intro:
        html = html[:match.start()] + modified + html[match.end():]
        logger.info("✅ Successfully split intro into 3 paragraphs")
    else:
        logger.warning("⚠️  Intro paragraph found but break points not matched")
    
    return html


def _reconstruct_animals_domestic_table(html: str) -> str:
    """
    Reconstruct the Animals, Domestic table from scattered paragraph data.
    
    The table should have 5 columns ("", "Erdlu", "Kank", "Mekillot", "Inix")
    and 22 rows covering all creature statistics.
    
    Args:
        html: The HTML content
        
    Returns:
        HTML with proper table structure
    """
    logger.info("Reconstructing Animals, Domestic table")
    
    try:
        # Find the Animals, Domestic header and the "There are numerous" paragraph
        animals_header_match = re.search(
            r'<p><span[^>]*><strong>Animals, Domestic</strong></span></p>',
            html
        )
        there_are_match = re.search(
            r'<p><span[^>]*>There are numerous domesticated animals',
            html
        )
        
        if not animals_header_match or not there_are_match:
            logger.warning("Could not find Animals, Domestic section boundaries")
            return html
        
        # Extract all content between header and "There are numerous"
        start_pos = animals_header_match.end()
        end_pos = there_are_match.start()
        section_content = html[start_pos:end_pos]
        
        # Define the table structure
        # Row labels (22 rows)
        row_labels = [
            "CLIMATE/TERRAIN:",
            "FREQUENCY",
            "ORGANIZATION:",
            "ACTIVITY CYCLE:",
            "DIET",
            "INTELLIGENCE:",
            "TREASURE:",
            "ALIGNMENT:",
            "NO. APPEARING:",
            "ARMOR CLASS:",
            "MOVEMENT",
            "HIT DICE:",
            "THAC0:",
            "NO. OF ATTACKS:",
            "DAMAGE/ATTACK:",
            "SPECIAL ATTACKS:",
            "SPECIAL DEFENSES:",
            "MAGIC RESISTANCE:",
            "SIZE:",
            "MORALE:",
            "XP VALUE:",
            "PSIONICS:"
        ]
        
        # Column headers (4 creatures) - order matches user specification
        creatures = ["Erdlu", "Kank", "Mekillot", "Inix"]
        
        # Hardcoded table data (extracted from the source)
        # Format: {row_label: {creature: value}}
        table_data = {
            "CLIMATE/TERRAIN:": {
                "Erdlu": "Tablelands<br>or Hinterlands",
                "Kank": "Tablelands<br>or Hinterlands",
                "Mekillot": "Tablelands<br>or Hinterlands",
                "Inix": "Tablelands<br>or Hinterlands"
            },
            "FREQUENCY": {
                "Erdlu": "Common",
                "Kank": "Common",
                "Mekillot": "Uncommon",
                "Inix": "Rare"
            },
            "ORGANIZATION:": {
                "Erdlu": "Flock",
                "Kank": "Hive",
                "Mekillot": "Solitary",
                "Inix": "Solitary"
            },
            "ACTIVITY CYCLE:": {
                "Erdlu": "Day",
                "Kank": "Any",
                "Mekillot": "Day",
                "Inix": "Day"
            },
            "DIET": {
                "Erdlu": "Omnivore",
                "Kank": "Omnivore",
                "Mekillot": "Herbivore",
                "Inix": "Omnivore"
            },
            "INTELLIGENCE:": {
                "Erdlu": "Animal (1)",
                "Kank": "Animal (1)",
                "Mekillot": "Animal (1)",
                "Inix": "Animal (1)"
            },
            "TREASURE:": {
                "Erdlu": "Nil",
                "Kank": "Nil",
                "Mekillot": "Nil",
                "Inix": "Nil"
            },
            "ALIGNMENT:": {
                "Erdlu": "Neutral",
                "Kank": "Neutral",
                "Mekillot": "Neutral",
                "Inix": "Neutral"
            },
            "NO. APPEARING:": {
                "Erdlu": "50-500<br>(5d10x10)",
                "Kank": "50-500<br>(5d10x10)",
                "Mekillot": "1 or 2",
                "Inix": "1 or 2"
            },
            "ARMOR CLASS:": {
                "Erdlu": "7",
                "Kank": "5",
                "Mekillot": "7 (underside 9)",
                "Inix": "4 (underside 9)"
            },
            "MOVEMENT": {
                "Erdlu": "18",
                "Kank": "15",
                "Mekillot": "15",
                "Inix": "9"
            },
            "HIT DICE:": {
                "Erdlu": "3",
                "Kank": "2",
                "Mekillot": "11",
                "Inix": "12"
            },
            "THAC0:": {
                "Erdlu": "17",
                "Kank": "19",
                "Mekillot": "9",
                "Inix": "9"
            },
            "NO. OF ATTACKS:": {
                "Erdlu": "2",
                "Kank": "1",
                "Mekillot": "2",
                "Inix": "1"
            },
            "DAMAGE/ATTACK:": {
                "Erdlu": "1d6",
                "Kank": "1d6/1d4",
                "Mekillot": "1d6/1d8",
                "Inix": "1d6"
            },
            "SPECIAL ATTACKS:": {
                "Erdlu": "Nil",
                "Kank": "See below",
                "Mekillot": "Crush",
                "Inix": "Swallow or crush"
            },
            "SPECIAL DEFENSES:": {
                "Erdlu": "Nil",
                "Kank": "Nil",
                "Mekillot": "Nil",
                "Inix": "Nil"
            },
            "MAGIC RESISTANCE:": {
                "Erdlu": "Nil",
                "Kank": "Nil",
                "Mekillot": "Nil",
                "Inix": "Nil"
            },
            "SIZE:": {
                "Erdlu": "M (7' tall)",
                "Kank": "L (8' long)",
                "Mekillot": "G (30' long)",
                "Inix": "H (16+' long)"
            },
            "MORALE:": {
                "Erdlu": "Average (10)",
                "Kank": "Elite (14)",
                "Mekillot": "Elite (14)",
                "Inix": "Steady (12)"
            },
            "XP VALUE:": {
                "Erdlu": "65",
                "Kank": "35",
                "Mekillot": "6,000",
                "Inix": "650"
            },
            "PSIONICS:": {
                "Erdlu": "Nil",
                "Kank": "Nil",
                "Mekillot": "Nil",
                "Inix": "Nil"
            }
        }
        
        # Build the HTML table
        table_html = '<table class="ds-table">\n'
        
        # Header row
        table_html += '  <tr>\n'
        table_html += '    <th></th>\n'
        for creature in creatures:
            table_html += f'    <th>{creature}</th>\n'
        table_html += '  </tr>\n'
        
        # Data rows
        for row_label in row_labels:
            table_html += '  <tr>\n'
            table_html += f'    <td><strong>{row_label}</strong></td>\n'
            for creature in creatures:
                value = table_data.get(row_label, {}).get(creature, "")
                table_html += f'    <td>{value}</td>\n'
            table_html += '  </tr>\n'
        
        table_html += '</table>\n'
        
        # Remove all the scattered paragraph content and malformed tables
        html = html[:start_pos] + '\n' + table_html + '\n' + html[end_pos:]
        
        logger.info("✅ Successfully reconstructed Animals, Domestic table")
        return html
        
    except Exception as e:
        logger.error(f"Failed to reconstruct Animals, Domestic table: {e}", exc_info=True)
        return html


def _format_creature_descriptions(html: str) -> str:
    """
    Format the creature descriptions after the Animals, Domestic table.
    
    Each creature should be an H2 header followed by properly broken paragraphs.
    
    Args:
        html: The HTML content
        
    Returns:
        HTML with properly formatted creature descriptions
    """
    logger.info("Formatting creature descriptions after Animals, Domestic table")
    
    try:
        # Find the "There are numerous" paragraph (may have spans)
        there_are_match = re.search(
            r'<p>(?:<span[^>]*>)?There are numerous domesticated animals',
            html
        )
        
        # Find the "Belgoi" header (the next major creature after domestic animals)
        belgoi_match = re.search(
            r'<p id="header-\d+-belgoi">',
            html
        )
        
        if not there_are_match or not belgoi_match:
            logger.warning(f"Could not find creature description boundaries (there_are={bool(there_are_match)}, belgoi={bool(belgoi_match)})")
            return html
        
        start_pos = there_are_match.start()
        end_pos = belgoi_match.start()
        
        # Build the formatted content with hardcoded creature descriptions
        formatted_html = '<p>There are numerous domesticated animals on Athas. Some of the most common ones, at least in the Hinter and Tablelands, are described here.</p>\n\n'
        
        # Erdlu (H2 + 3 paragraphs)
        formatted_html += '<h2>Erdlu</h2>\n'
        formatted_html += '<p>Erdlus are flightless, featherless birds covered with flaky gray-to-red scales. They weigh as much as 200 pounds and stand up to seven feet tall. They have powerful, lanky legs ending in four-toed feet with razor-sharp claws, and can run at great speeds over short distances (no more than half-a-mile). Their bodies are massive and round, with a pair of useless wings folded at their sides. Attached to their yellow, snake-like necks are small round heads with huge wedge-shaped beaks.</p>\n'
        formatted_html += '<p>Erdlus make ideal herd animals, as they can eat many forms of tough vegetation, as well as snakes, lizards, and other small reptiles. They instinctively band together in flocks for protection. When threatened, their first impulse is to flee. If this is not possible, the entire flock will turn and give battle as a group. When they fight, they strike at their attackers with their sharp beaks and then rake them with their claws.</p>\n'
        formatted_html += '<p>Erdlu eggs are an excellent food, containing all the nutrients that a human or demihuman needs to survive for months at a time. If eaten raw, they can even substitute for water (1 gallon per egg) for periods of up to one week. In addition, the hard scales of their wings make excellent shields or armor (AC 6), their beaks can be used to make fine spearheads, and their claws are often crafted into daggers or tools.</p>\n\n'
        
        # Kank (H2 + 6 paragraphs)
        formatted_html += '<h2>Kank</h2>\n'
        formatted_html += '<p>Kanks are large docile insects. Their bodies have a black chitinous exoskeleton, and are divided into three sections: head, thorax, and abdomen. Kanks often weigh as much as 400 pounds and stand up to four feet tall at the back, with bodies as long as eight feet from head to abdomen. Around their mouths, they have a pair of multi-jointed pincers which they use to carry objects, to feed themselves, and occasionally to fight with. On their thoraxes, they have six lanky legs ending in a single flexible claw with which the kank can grip the surfaces it walks upon. Their bulbous abdomens have no appendages, and are simply carried above the ground.</p>\n'
        formatted_html += '<p>Kanks are often used as caravan mounts, as they can travel for a full day at their top speed, carrying a two-hundred pound passenger and two-hundred pounds of cargo. They also make decent herd animals and are especially valued by elves. Because they can digest nearly any sort of organic matter, these hardy beasts will thrive in almost any environment. In addition, they require little attention, for a kank hive instinctively organizes itself into food producers, soldiers, and brood queens.</p>\n'
        formatted_html += '<p>The food producers secrete melon-sized globules of green honey that they store on the their abdomens to feed the young and, when food is scarce, the rest of the hive. Humans and demihumans can live on this nectar alone for periods of up to three weeks, but must supplement their diets with meat and/or vegetation after longer periods. The sweet taste of this nectar makes it very valuable, and it is this that has caused the kank to be domesticated. It should be noted that wild kanks produce far fewer globules than their carefully breed cousins.</p>\n'
        formatted_html += '<p>When the tribe stops in an area that looks as though there is a considerable amount of vegetation, the brood queens lay a clutch of twenty to fifty eggs. The soldier kanks, along with the rest of the hive, ferociously defend this area from all predators, and will not leave until the eggs hatch. Herders must delay their migrations or abandon their hives when this conflicts with their plans.</p>\n'
        formatted_html += '<p>In a fight, the soldiers attack first, striking with their pincers for 1d6 points of damage. In addition, any victim hit by a soldier is injected with Class O poison (save vs. poison or be paralyzed in 2d12 rounds). If pressed, the food producers will also fight, but they lack the poison of the soldiers. The brood queen never attacks, even in self defense.</p>\n'
        formatted_html += '<p>Although predators may attack kanks for the food producers\' honey globules, only the foulest carrion eaters will eat kank flesh. As soon as a kank dies, its meat emits a foul-smelling odor that not even a starving man can stomach. The chitinous exoskeleton of kanks can be scraped and cut into solid plates of armor (AC5), but it is somewhat brittle and each time it is hit there is a 20% chance that it will shatter.</p>\n\n'
        
        # Mekillot (H2 + 4 paragraphs)
        formatted_html += '<h2>Mekillot</h2>\n'
        formatted_html += '<p>Mekillots are mighty lizards weighing up to six-tons, with huge, mound-shaped bodies as long as 30 feet. Their backs and heads are covered with a thick shell that serves as both a sunshade and protection from attacks by other large creatures. Their undersides are covered with much softer scales (AC 8).</p>\n'
        formatted_html += '<p>Despite their vicious dispositions, mekillots are often used as caravan beasts. A hitched pair can pull a wagon weighing 10-20 tons at a slow, plodding pace. Mekillots are never truly tame, however; even when they are hitched to a wagon, the stubborn creatures have been known to turn off the road and go wandering off for days -- without any apparent reason. They are also noted for making snacks of their handlers. Because of the difficulties of controlling these beasts, most caravans rely on psionicists with the appropriate powers to drive them.</p>\n'
        formatted_html += '<p>In a fight, mekillots attack with their long tongues, striking for 1d6 damage. On a natural roll of 20, the tongue grasps the victim and tries to draw him into his mouth. He must save vs. paralyzation to avoid being swallowed and slowly killed by the great beast\'s digestive system. Swallowed individuals are helpless to employ any form of attack other than psionics on the mekillot that consumed them.</p>\n'
        formatted_html += '<p>Mekillots protect their vulnerable undersides by instinctively dropping to their bellies when anything crawls beneath them. This causes 2d12 points of damage to the creature they drop upon and may injure the mekillot, depending on what it is trying to flatten.</p>\n\n'
        
        # Inix (H2 + 3 paragraphs) - note user said 3 paragraphs with breaks at "Inix make", "The one major", "In combat"
        formatted_html += '<h2>Inix</h2>\n'
        formatted_html += '<p>The inix is a large lizard midway in size between a kank and mekillot. It weighs about two tons and grows up to sixteen feet long. Its back is protected by a thick shell, while its belly is covered with a layer of flexible scales.</p>\n'
        formatted_html += '<p>Inix make spirited mounts, and are capable of carrying up to a seven-hundred and fifty pounds. They move at steady pace for hours on end, and over short distances, their charge is as fast as that of a kank. Inix riders often travel in howdahs, small box-like carriages that are strapped to the beast\'s back.</p>\n'
        formatted_html += '<p>The one major drawback to traveling by inix is that these large herbivores need vast amounts of forage. If they don\'t get enough to eat they are nearly impossible to control. Thus, they are seldom used in regions where forage is at a premium.</p>\n'
        formatted_html += '<p>In combat, inix slap with their immense tail (1d6 damage) and bite (1d8 damage). On a natural biting attack roll of 20, they grasp man-sized or smaller opponents and do an additional 1d20 points of crushing damage. Their shells are useful for making armor (AC 5), and their scaly underbellies can be used to make a type of fine leather armor (AC7).</p>\n\n'
        
        # Replace the section
        html = html[:start_pos] + formatted_html + html[end_pos:]
        
        logger.info("✅ Successfully formatted creature descriptions")
        return html
        
    except Exception as e:
        logger.error(f"Failed to format creature descriptions: {e}", exc_info=True)
        return html


def postprocess_chapter_five_monsters(html: str) -> str:
    """
    Apply all HTML post-processing for Chapter Five: Monsters of Athas.
    
    Args:
        html: The HTML content
        
    Returns:
        Processed HTML content
    """
    logger.info("Postprocessing Chapter Five: Monsters of Athas HTML")
    
    # Apply intro paragraph breaks
    html = apply_intro_paragraph_breaks(html)
    
    # Reconstruct Animals, Domestic table
    html = _reconstruct_animals_domestic_table(html)
    
    # Format creature descriptions
    html = _format_creature_descriptions(html)
    
    # Reconstruct all monster manual pages
    html = reconstruct_all_monster_pages(html)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html = convert_all_styled_headers_to_semantic(html)
    
    return html

