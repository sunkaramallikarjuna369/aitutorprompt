from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class StudentMode(str, Enum):
    DULL = "dull"
    AVERAGE = "average"
    CLEVER = "clever"


class AnimationConfig(BaseModel):
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Animation speed multiplier")
    easing: str = Field(default="easeInOut", description="Animation easing function")
    duration_ms: int = Field(default=1000, ge=100, le=5000, description="Animation duration in milliseconds")
    auto_play: bool = Field(default=True, description="Whether to auto-play animations")
    loop: bool = Field(default=False, description="Whether to loop animations")


class AxisConfig(BaseModel):
    show: bool = Field(default=True)
    color: str = Field(default="#333333")
    label_size: int = Field(default=12, ge=8, le=24)
    grid_lines: bool = Field(default=True)
    grid_color: str = Field(default="#e0e0e0")
    emphasis: str = Field(default="normal", description="none, normal, high")


class ColorScheme(BaseModel):
    primary: str = Field(default="#3b82f6", description="Primary color for main elements")
    secondary: str = Field(default="#10b981", description="Secondary color for highlights")
    background: str = Field(default="#ffffff", description="Background color")
    text: str = Field(default="#1f2937", description="Text color")
    accent: str = Field(default="#f59e0b", description="Accent color for emphasis")
    error: str = Field(default="#ef4444", description="Error/negative color")
    success: str = Field(default="#22c55e", description="Success/positive color")


class ScaffoldingConfig(BaseModel):
    level: str = Field(default="medium", description="none, low, medium, high")
    show_hints: bool = Field(default=True)
    show_step_numbers: bool = Field(default=True)
    highlight_key_points: bool = Field(default=True)
    use_metaphors: bool = Field(default=False)
    metaphor_type: Optional[str] = Field(default=None, description="Type of real-world metaphor to use")


class InteractivityConfig(BaseModel):
    sandbox_mode: bool = Field(default=False, description="Allow free exploration")
    slider_controls: bool = Field(default=True)
    click_to_explore: bool = Field(default=True)
    drag_enabled: bool = Field(default=False)
    zoom_enabled: bool = Field(default=False)
    reset_button: bool = Field(default=True)


class AdvancedFeatures(BaseModel):
    show_discriminant: bool = Field(default=False)
    show_complex_roots: bool = Field(default=False)
    show_3d_transformation: bool = Field(default=False)
    show_derivative: bool = Field(default=False)
    show_integral: bool = Field(default=False)
    stress_test_mode: bool = Field(default=False)


class VisualConfig(BaseModel):
    topic_id: str
    student_mode: StudentMode
    visualization_type: str = Field(default="parabola", description="Type of visualization")
    title: str = Field(default="Quadratic Equation Visualization")
    description: str = Field(default="Interactive visualization of quadratic equations")
    
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    x_axis: AxisConfig = Field(default_factory=AxisConfig)
    y_axis: AxisConfig = Field(default_factory=AxisConfig)
    colors: ColorScheme = Field(default_factory=ColorScheme)
    scaffolding: ScaffoldingConfig = Field(default_factory=ScaffoldingConfig)
    interactivity: InteractivityConfig = Field(default_factory=InteractivityConfig)
    advanced: AdvancedFeatures = Field(default_factory=AdvancedFeatures)
    
    initial_values: Dict[str, float] = Field(
        default_factory=lambda: {"a": 1.0, "b": 0.0, "c": 0.0},
        description="Initial coefficient values"
    )
    
    value_ranges: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "a": {"min": -5.0, "max": 5.0, "step": 0.1},
            "b": {"min": -10.0, "max": 10.0, "step": 0.5},
            "c": {"min": -10.0, "max": 10.0, "step": 0.5}
        },
        description="Allowed ranges for coefficient sliders"
    )
    
    annotations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Additional annotations to display"
    )
    
    pedagogical_notes: List[str] = Field(
        default_factory=list,
        description="Teaching notes for the visualization"
    )


class AIPromptTemplate(BaseModel):
    mode: StudentMode
    system_prompt: str
    user_prompt_template: str
    
    @classmethod
    def get_dull_template(cls) -> "AIPromptTemplate":
        return cls(
            mode=StudentMode.DULL,
            system_prompt="""You are an educational AI assistant specializing in creating visual configurations 
for mathematics learning. Your task is to generate JSON configurations that help struggling students 
understand quadratic equations through simplified, highly scaffolded visualizations.""",
            user_prompt_template="""Generate a simplified, high-scaffolding visual configuration for a 14-year-old 
struggling with math. Use concrete real-world metaphors (e.g., a ball's path). Slow down animation speeds 
and use bright, high-contrast visual cues for the X and Y axis.

Topic: {topic_name}
Learning Objectives: {learning_objectives}
Student's Current Mastery: {mastery_level}%

Generate a JSON configuration following this schema:
- Use animation speed of 0.5x or slower
- Use high-contrast colors (bright primary colors)
- Enable all scaffolding features
- Use simple metaphors like "ball trajectory" or "bridge arch"
- Disable advanced features like discriminant or complex roots
- Add step-by-step pedagogical notes

Return only valid JSON matching the VisualConfig schema."""
        )
    
    @classmethod
    def get_average_template(cls) -> "AIPromptTemplate":
        return cls(
            mode=StudentMode.AVERAGE,
            system_prompt="""You are an educational AI assistant specializing in creating visual configurations 
for mathematics learning. Your task is to generate JSON configurations that help average students 
understand quadratic equations through balanced, procedural visualizations.""",
            user_prompt_template="""Generate a balanced procedural visualization. Focus on the relationship 
between the quadratic formula variables and the parabola's movement. Use standard mathematical color coding.

Topic: {topic_name}
Learning Objectives: {learning_objectives}
Student's Current Mastery: {mastery_level}%

Generate a JSON configuration following this schema:
- Use normal animation speed (1.0x)
- Use standard mathematical color coding (blue for positive, red for negative)
- Enable medium scaffolding
- Show the connection between coefficients and graph properties
- Enable discriminant visualization
- Add procedural pedagogical notes

Return only valid JSON matching the VisualConfig schema."""
        )
    
    @classmethod
    def get_clever_template(cls) -> "AIPromptTemplate":
        return cls(
            mode=StudentMode.CLEVER,
            system_prompt="""You are an educational AI assistant specializing in creating visual configurations 
for mathematics learning. Your task is to generate JSON configurations that challenge advanced students 
with complex, abstract visualizations of quadratic equations.""",
            user_prompt_template="""Generate a complex, abstract visualization. Include the discriminant's impact 
on complex roots and 3D transformations. Provide a 'sandbox' mode where the student can stress-test 
the limits of the equation.

Topic: {topic_name}
Learning Objectives: {learning_objectives}
Student's Current Mastery: {mastery_level}%

Generate a JSON configuration following this schema:
- Use faster animation speed (1.5x-2.0x)
- Use sophisticated color gradients
- Disable scaffolding or set to minimal
- Enable sandbox/exploration mode
- Enable all advanced features (discriminant, complex roots, 3D transformations)
- Enable stress-test mode for edge cases
- Add advanced mathematical insights as pedagogical notes

Return only valid JSON matching the VisualConfig schema."""
        )
    
    @classmethod
    def get_template_for_mode(cls, mode: StudentMode) -> "AIPromptTemplate":
        templates = {
            StudentMode.DULL: cls.get_dull_template,
            StudentMode.AVERAGE: cls.get_average_template,
            StudentMode.CLEVER: cls.get_clever_template,
        }
        return templates[mode]()


class RWALNarrativeRequest(BaseModel):
    topic_id: str
    student_mode: StudentMode
    context: Optional[str] = None
    region: Optional[str] = None


class RWALNarrative(BaseModel):
    topic_id: str
    student_mode: StudentMode
    title: str
    narrative: str
    real_world_scenario: str
    daily_life_examples: List[str]
    industry_applications: List[str]
    career_connections: List[str]
    mini_project_ideas: List[str]
    difficulty_level: str


class QuizQuestionRequest(BaseModel):
    topic_id: str
    bloom_level: str
    difficulty: str
    student_mode: StudentMode
    count: int = 1


class GeneratedQuizQuestion(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    hint: str
    bloom_level: str
    difficulty: str
