<!--
This is the main track file for the Conductor extension.
It's used to define and manage different development plans or "tracks".

You can define a track like this:

@track "Your Track Name" {
  // Path to the detailed plan for this track
  plan = "conductor/tracks/your_track_name/plan.md" 
  
  // (Optional) Glob patterns for files relevant to this track
  files = ["src/**/*.py", "apps/tax_assistant.py"]
}

-->

# Development Tracks

This file outlines the different development plans for the PJJ Tax & Legal AI System.
Each track represents a distinct goal or feature.

@track "Initial Setup" {
  plan = "conductor/tracks/initial_setup/plan.md"
  status = "completed"
}

@track "Migrate from Fireworks AI to Google Gemini 3.0" {
  plan = "conductor/tracks/gemini_migration_20251227/plan.md"
  status = "cancelled"
}

@track "Refactor to use Vertex AI Authentication" {
  plan = "conductor/tracks/vertex_ai_auth_20251227/plan.md"
  status = "cancelled"
}

@track "Fix NameError in src/pjj_tax_legal/agent/model.py" {
  plan = "conductor/tracks/fix_nameerror_20251228/plan.md"
  status = "cancelled"
}

@track "Refactor searcher.py to use Gemini and add fallback" {
  plan = "conductor/tracks/searcher_refactor_20251228/plan.md"
  status = "cancelled"
}

@track "Refactor searcher.py with Gemini and \"Anti-Zero\" Fallback" {
  plan = "conductor/tracks/searcher_refactor_v2_20251228/plan.md"
  status = "cancelled"
}

