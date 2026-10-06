# Vish's mascot: instructions for Claude

Use the supplied mascot consistently in my LinkedIn posts, carousels and videos. The reference is the adult 3D-style character on the right of my example post.

## Paste this into Claude

“Treat the attached character sheets and PNGs as my established mascot. Keep his face, age, brown skin tone, wavy dark brown hair, tortoiseshell glasses, moustache, goatee, earring, necklace, ivory blazer, burgundy shirt, indigo jeans and brown boots consistent. Choose an existing pose or expression to match the content. Use the actual PNG where possible. Do not replace him with a generic character or recreate his face with SVG, CSS or simple shapes. Preserve the 3D rendering and the transparent background.

For a post with the mascot on the right and content on the left, choose point_screen_left. For the opposite layout, choose point_screen_right. Use explaining or present_screen_right for a process or chart, thinking or skeptical for a tradeoff, focused for analysis, surprised for unexpected news, and thumbs_up or pleased for a positive conclusion. Use arms_crossed as the default signature pose.

Keep the mascot secondary to the information. Match his gaze and gesture to the content. Leave space around his hands and hair, preserve his proportions, and keep him clear of headlines and labels. Keep emotions restrained enough for professional posts. Use rear and profile views only when the composition needs them.

For motion, animate the existing PNG with small position, scale or opacity changes, or use the wave keyframes as pose references. These are raster images with 3D styling, not a rotatable 3D model or a rigged character. A rotation preview cycles through eight separate views. Do not claim that an image sequence supplies smooth 3D rotation, lip sync or skeletal animation.

If creating a new angle or action with an image-generation tool, use the original identity reference and the nearest existing pose together. Keep the same face, clothing and adult proportions. Check the fingers, glasses, hair and boots before using the output. If you cannot access the actual PNG in the rendering environment, ask for that file or explain what asset input is missing.”

## Upload and use

On iPad, download and tap the ZIP in Files to extract it. Start with the four PNGs in `00_reference_sheets` and this guide as visual references. Attach the individual PNGs needed for the specific post or scene. The reference PDF provides a labelled overview of all 31 assets.

The individual PNGs have real alpha transparency. Full-body assets are standardized to 512 × 768 px; portraits are 512 × 512 px. They were cropped and resized from the generated sheets, so resizing does not add new detail. The sheets retain their original rendered dimensions. For a large close-up or a post dominated by the mascot, generate a larger single-pose render from the identity reference rather than stretching a small crop excessively.

## Files

| Folder | Contents |
| --- | --- |
| `00_reference_sheets` | Four complete sheets: all sides, expressions, gestures, wave keyframes |
| `01_angles` | Eight full-body views from front, sides and rear |
| `02_expressions` | Nine head-and-shoulder expressions |
| `03_gestures` | Eight full-body presenter poses |
| `04_wave_keyframes` | Six separate wave poses |
| `05_previews` | Stepped turnaround and wave GIF previews |

Left and right in filenames mean the direction on the screen, not the character's anatomical left and right. Angle names describe the visible view; they are not calibrated camera measurements. The source cells and recommended uses are listed in `asset_manifest.json`.

The source images are generated variations, so small differences between views remain. Keep this set as the approved reference rather than repeatedly redesigning the mascot. The original reference remains the authority for any new render.
