# Chapter 2 Changelog

## 2025-11-08
- Locked Chapter 2 (“Player Character Races”) from transformation by adding `chapter-two-player-character-races` to `skip_slugs` in `data/mappings/section_profiles.json`, per CONTENT_LOCK policy. This preserves current processed JSON/HTML as the source of truth.

## 2025-11-08
- Fixed table header labels rendering as document headers in “Starting Age” and “Aging Effects”:
  - After reconstructing each table, the transformer now clears header label lines within the section bounds so they do not appear as H1/H2/H3/H4 headers in HTML.
  - Starting Age: removes “Race”, “Base Age”, “Variable”, “(Base + Variable)”, and “Maximum Age Range”.
  - Aging Effects: removes “Race”/“R a c e”, “Middle Age*”, “Old Age**”, and “Venerable***”.
- Result: no stray “Maximum Age Range”, “Base Age”, etc., appearing as document headers; table headers are rendered only within `<th>` cells with distinct styling.


