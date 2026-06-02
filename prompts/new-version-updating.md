As our resident engineering and automation expert, I need you to audit and update our Python scripts that automate .3mf file creation and modification. 

Bambu Studio has officially shifted from Beta Branch V2.7.0.50 to Public Release V2.7.1.57. Because Bambu Lab fundamentally overhauled the machine preset configurations, configuration placeholders, and the backend architecture for the Filament Manager in this release, our existing 3MF modification scripts are highly susceptible to breaking.

Please review our Python scripts in this workspace and update them to ensure full compatibility with V2.7.1.57.

### PRE-COMPUTED RESEARCH & RECONNAISSANCE
To save you time, here is the technical breakdown of what changed in the V2.7.1.57 release cycle regarding the .3mf archive:

1. Archive Structure Impact: A Bambu Studio 3MF is a zipped archive containing XML and text config data (e.g., `Metadata/Bambu_Cloud.config`, `Metadata/slice_info.config`, and `3D/3dmodel.model`). 
2. Machine Preset Changes: Bambu Lab explicitly added new machine preset configurations, underlying schema structural constraints, and new text placeholders. Old hardcoded text strings, dictionary keys, or regex expressions targeting legacy config tags will likely cause a KeyError or slice validation error.
3. Filament Manager Architecture: The backend indexing for filament slots changed to support expanded slot counts (up to 32 slots). Scripted injections that hardcode filament slot indices or legacy material strings must be audited to prevent Bambu Studio from resetting the profile to default values upon ingestion.
4. Archive Validation: Ensure our zip writing implementation (e.g., using python's zipfile module with ZIP_DEFLATED or ZIP_STORED) preserves archive integrity exactly as expected by the new public release build.

### YOUR TASKS:
1. Scan the current repository for any scripts handling 3MF zip extraction, text/XML parsing, regex matching on slicer configurations, or filament mapping.
2. If you need to verify exact schema changes, write a quick, temporary script to run a differential analysis between a 2.7.0.50 beta 3MF file and a 2.7.1.57 public 3MF file (extracting and diffing their `Metadata/` configs) to pinpoint exact key renamings.
3. Update all hardcoded config keys, dictionary pathways, or search patterns to match the new V2.7.1.57 placeholder conventions.
4. Ensure robust error handling so that if a key is missing, the script gracefully alerts the user instead of outputting a silently corrupted 3MF file that causes Bambu Studio to flush changes back to factory defaults.

Please review the codebase, explain your plan of action, and execute the necessary refactoring.
