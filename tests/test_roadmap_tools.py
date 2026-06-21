from tools.roadmap_tools import RoadmapTools

def test_format_phase():
    phase_num = 1
    phase_title = "Basics"
    tasks = ["Task A", "Task B"]
    
    formatted = RoadmapTools.format_phase(phase_num, phase_title, tasks)
    
    assert "Phase 1: Basics" in formatted
    assert "- [ ] **Day 1:** Task A" in formatted
    assert "- [ ] **Day 2:** Task B" in formatted

def test_parse_tasks_by_week():
    tasks = RoadmapTools.parse_tasks_by_week("")
    assert "Week 1" in tasks
    assert "Week 4" in tasks
    assert len(tasks["Week 1"]) > 0
