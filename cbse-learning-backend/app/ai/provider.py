from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import os
import logging

from .schemas import (
    VisualConfig, StudentMode, AIPromptTemplate,
    RWALNarrative, RWALNarrativeRequest,
    GeneratedQuizQuestion, QuizQuestionRequest,
    AnimationConfig, AxisConfig, ColorScheme,
    ScaffoldingConfig, InteractivityConfig, AdvancedFeatures
)

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    @abstractmethod
    async def generate_visual_config(
        self,
        topic_id: str,
        topic_name: str,
        learning_objectives: list[str],
        student_mode: StudentMode,
        mastery_level: float = 50.0
    ) -> VisualConfig:
        pass
    
    @abstractmethod
    async def generate_rwal_narrative(
        self,
        request: RWALNarrativeRequest,
        topic_name: str,
        base_scenarios: list[dict]
    ) -> RWALNarrative:
        pass
    
    @abstractmethod
    async def generate_quiz_questions(
        self,
        request: QuizQuestionRequest,
        topic_name: str,
        existing_questions: list[dict]
    ) -> list[GeneratedQuizQuestion]:
        pass
    
    @abstractmethod
    async def generate_worked_example(
        self,
        topic_id: str,
        problem: str,
        student_mode: StudentMode
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text response for RAG and general queries."""
        pass


class MockAIProvider(AIProvider):
    async def generate_visual_config(
        self,
        topic_id: str,
        topic_name: str,
        learning_objectives: list[str],
        student_mode: StudentMode,
        mastery_level: float = 50.0
    ) -> VisualConfig:
        logger.info(f"MockAIProvider: Generating visual config for {topic_id} in {student_mode} mode")
        
        if student_mode == StudentMode.DULL:
            return VisualConfig(
                topic_id=topic_id,
                student_mode=student_mode,
                visualization_type="parabola",
                title=f"Understanding {topic_name} - Step by Step",
                description="A simplified visualization using real-world examples to help you understand quadratic equations",
                animation=AnimationConfig(
                    speed=0.5,
                    easing="easeInOut",
                    duration_ms=2000,
                    auto_play=True,
                    loop=True
                ),
                x_axis=AxisConfig(
                    show=True,
                    color="#FF6B6B",
                    label_size=16,
                    grid_lines=True,
                    grid_color="#FFE0E0",
                    emphasis="high"
                ),
                y_axis=AxisConfig(
                    show=True,
                    color="#4ECDC4",
                    label_size=16,
                    grid_lines=True,
                    grid_color="#E0FFFC",
                    emphasis="high"
                ),
                colors=ColorScheme(
                    primary="#FF6B6B",
                    secondary="#4ECDC4",
                    background="#FFF9F0",
                    text="#2C3E50",
                    accent="#FFE66D",
                    error="#E74C3C",
                    success="#2ECC71"
                ),
                scaffolding=ScaffoldingConfig(
                    level="high",
                    show_hints=True,
                    show_step_numbers=True,
                    highlight_key_points=True,
                    use_metaphors=True,
                    metaphor_type="ball_trajectory"
                ),
                interactivity=InteractivityConfig(
                    sandbox_mode=False,
                    slider_controls=True,
                    click_to_explore=True,
                    drag_enabled=False,
                    zoom_enabled=False,
                    reset_button=True
                ),
                advanced=AdvancedFeatures(
                    show_discriminant=False,
                    show_complex_roots=False,
                    show_3d_transformation=False,
                    show_derivative=False,
                    show_integral=False,
                    stress_test_mode=False
                ),
                initial_values={"a": 1.0, "b": 0.0, "c": -4.0},
                value_ranges={
                    "a": {"min": -3.0, "max": 3.0, "step": 0.5},
                    "b": {"min": -5.0, "max": 5.0, "step": 1.0},
                    "c": {"min": -5.0, "max": 5.0, "step": 1.0}
                },
                annotations=[
                    {"type": "label", "text": "Think of this as a ball's path!", "position": "top"},
                    {"type": "highlight", "element": "vertex", "color": "#FFE66D"},
                    {"type": "arrow", "from": "vertex", "to": "roots", "label": "The ball lands here!"}
                ],
                pedagogical_notes=[
                    "Imagine throwing a ball - it goes up, then comes down in a curved path",
                    "The highest point is called the vertex - like the top of the ball's arc",
                    "Where the curve touches the ground are the roots - where the ball lands",
                    "The 'a' value controls how wide or narrow the curve is",
                    "Try changing the values slowly and watch what happens!"
                ]
            )
        
        elif student_mode == StudentMode.AVERAGE:
            return VisualConfig(
                topic_id=topic_id,
                student_mode=student_mode,
                visualization_type="parabola",
                title=f"Exploring {topic_name}",
                description="Interactive visualization showing the relationship between coefficients and the parabola",
                animation=AnimationConfig(
                    speed=1.0,
                    easing="easeInOut",
                    duration_ms=1000,
                    auto_play=True,
                    loop=False
                ),
                x_axis=AxisConfig(
                    show=True,
                    color="#3B82F6",
                    label_size=14,
                    grid_lines=True,
                    grid_color="#E5E7EB",
                    emphasis="normal"
                ),
                y_axis=AxisConfig(
                    show=True,
                    color="#3B82F6",
                    label_size=14,
                    grid_lines=True,
                    grid_color="#E5E7EB",
                    emphasis="normal"
                ),
                colors=ColorScheme(
                    primary="#3B82F6",
                    secondary="#10B981",
                    background="#FFFFFF",
                    text="#1F2937",
                    accent="#F59E0B",
                    error="#EF4444",
                    success="#22C55E"
                ),
                scaffolding=ScaffoldingConfig(
                    level="medium",
                    show_hints=True,
                    show_step_numbers=True,
                    highlight_key_points=True,
                    use_metaphors=False,
                    metaphor_type=None
                ),
                interactivity=InteractivityConfig(
                    sandbox_mode=False,
                    slider_controls=True,
                    click_to_explore=True,
                    drag_enabled=True,
                    zoom_enabled=True,
                    reset_button=True
                ),
                advanced=AdvancedFeatures(
                    show_discriminant=True,
                    show_complex_roots=False,
                    show_3d_transformation=False,
                    show_derivative=False,
                    show_integral=False,
                    stress_test_mode=False
                ),
                initial_values={"a": 1.0, "b": -2.0, "c": -3.0},
                value_ranges={
                    "a": {"min": -5.0, "max": 5.0, "step": 0.25},
                    "b": {"min": -10.0, "max": 10.0, "step": 0.5},
                    "c": {"min": -10.0, "max": 10.0, "step": 0.5}
                },
                annotations=[
                    {"type": "formula", "text": "y = ax² + bx + c", "position": "top-right"},
                    {"type": "highlight", "element": "discriminant", "color": "#F59E0B"},
                    {"type": "label", "text": "Discriminant: b² - 4ac", "position": "bottom"}
                ],
                pedagogical_notes=[
                    "The coefficient 'a' determines if the parabola opens up (a > 0) or down (a < 0)",
                    "The coefficient 'b' shifts the parabola left or right",
                    "The coefficient 'c' is the y-intercept (where the curve crosses the y-axis)",
                    "The discriminant (b² - 4ac) tells us about the nature of roots",
                    "When discriminant > 0: two real roots, = 0: one root, < 0: no real roots"
                ]
            )
        
        else:
            return VisualConfig(
                topic_id=topic_id,
                student_mode=student_mode,
                visualization_type="parabola_advanced",
                title=f"Advanced Analysis: {topic_name}",
                description="Complex visualization with discriminant analysis, complex roots, and 3D transformations",
                animation=AnimationConfig(
                    speed=1.5,
                    easing="easeOut",
                    duration_ms=500,
                    auto_play=False,
                    loop=False
                ),
                x_axis=AxisConfig(
                    show=True,
                    color="#6366F1",
                    label_size=12,
                    grid_lines=True,
                    grid_color="#F3F4F6",
                    emphasis="none"
                ),
                y_axis=AxisConfig(
                    show=True,
                    color="#6366F1",
                    label_size=12,
                    grid_lines=True,
                    grid_color="#F3F4F6",
                    emphasis="none"
                ),
                colors=ColorScheme(
                    primary="#6366F1",
                    secondary="#8B5CF6",
                    background="#0F172A",
                    text="#F8FAFC",
                    accent="#22D3EE",
                    error="#F43F5E",
                    success="#34D399"
                ),
                scaffolding=ScaffoldingConfig(
                    level="none",
                    show_hints=False,
                    show_step_numbers=False,
                    highlight_key_points=False,
                    use_metaphors=False,
                    metaphor_type=None
                ),
                interactivity=InteractivityConfig(
                    sandbox_mode=True,
                    slider_controls=True,
                    click_to_explore=True,
                    drag_enabled=True,
                    zoom_enabled=True,
                    reset_button=True
                ),
                advanced=AdvancedFeatures(
                    show_discriminant=True,
                    show_complex_roots=True,
                    show_3d_transformation=True,
                    show_derivative=True,
                    show_integral=True,
                    stress_test_mode=True
                ),
                initial_values={"a": 1.0, "b": 0.0, "c": 1.0},
                value_ranges={
                    "a": {"min": -10.0, "max": 10.0, "step": 0.1},
                    "b": {"min": -20.0, "max": 20.0, "step": 0.1},
                    "c": {"min": -20.0, "max": 20.0, "step": 0.1}
                },
                annotations=[
                    {"type": "formula", "text": "Roots: x = (-b ± √(b²-4ac)) / 2a", "position": "top-right"},
                    {"type": "complex_plane", "show": True},
                    {"type": "derivative", "text": "dy/dx = 2ax + b", "position": "bottom-right"}
                ],
                pedagogical_notes=[
                    "Explore the relationship between the discriminant and the nature of roots in the complex plane",
                    "When Δ < 0, roots become complex conjugates: x = (-b ± i√|Δ|) / 2a",
                    "The vertex form y = a(x-h)² + k reveals the transformation from y = x²",
                    "The derivative 2ax + b = 0 gives the x-coordinate of the vertex",
                    "Challenge: Find coefficient values that produce specific root patterns"
                ]
            )
    
    async def generate_rwal_narrative(
        self,
        request: RWALNarrativeRequest,
        topic_name: str,
        base_scenarios: list[dict]
    ) -> RWALNarrative:
        logger.info(f"MockAIProvider: Generating RWAL narrative for {request.topic_id} in {request.student_mode} mode")
        
        if request.student_mode == StudentMode.DULL:
            return RWALNarrative(
                topic_id=request.topic_id,
                student_mode=request.student_mode,
                title=f"Real-World Fun with {topic_name}",
                narrative="""Have you ever thrown a ball to a friend? Or watched water come out of a fountain? 
                These everyday things follow a special curved path called a parabola! 
                When you understand quadratic equations, you can predict exactly where that ball will land 
                or how high the water will go. It's like having a superpower to see the future of moving things!""",
                real_world_scenario="Imagine you're playing catch with your friend. When you throw the ball, "
                "it goes up, reaches a highest point, and then comes down. This path is a parabola! "
                "The harder you throw (bigger 'a'), the steeper the curve. Cool, right?",
                daily_life_examples=[
                    "Throwing a ball to your friend",
                    "Water fountains in parks",
                    "Jumping on a trampoline",
                    "Kicking a football",
                    "Pouring water from a bottle"
                ],
                industry_applications=[
                    "Video game designers use parabolas to make characters jump realistically",
                    "Toy makers design ball launchers using these curves",
                    "Playground designers create safe slides using parabolic shapes"
                ],
                career_connections=[
                    "Game Designer - Create fun jumping mechanics in video games",
                    "Sports Coach - Help athletes throw and kick better",
                    "Toy Designer - Make awesome ball launchers and water toys"
                ],
                mini_project_ideas=[
                    "Build a paper ball launcher and measure where balls land",
                    "Record yourself throwing a ball and trace its path",
                    "Design a mini golf hole using parabolic curves"
                ],
                difficulty_level="beginner"
            )
        
        elif request.student_mode == StudentMode.AVERAGE:
            return RWALNarrative(
                topic_id=request.topic_id,
                student_mode=request.student_mode,
                title=f"Applications of {topic_name}",
                narrative="""Quadratic equations are everywhere in the real world! From the graceful arches 
                of bridges to the trajectory of a basketball, parabolas shape our world. Engineers use 
                these equations to design structures, physicists use them to predict motion, and economists 
                use them to model profit and loss. Understanding quadratics opens doors to many fields.""",
                real_world_scenario="Consider a suspension bridge like the Golden Gate Bridge. The main cables "
                "hang in a parabolic shape due to the uniform weight distribution. Engineers use quadratic "
                "equations to calculate the exact shape needed to support the bridge safely.",
                daily_life_examples=[
                    "The arc of a basketball shot",
                    "Satellite dish shapes for TV reception",
                    "Car headlight reflectors",
                    "The path of a diver off a diving board",
                    "Profit calculations in business"
                ],
                industry_applications=[
                    "Civil Engineering - Bridge and arch design",
                    "Automotive - Headlight and mirror design",
                    "Telecommunications - Satellite dish optimization",
                    "Sports Science - Trajectory analysis for athletes"
                ],
                career_connections=[
                    "Civil Engineer - Design bridges and structures using parabolic principles",
                    "Data Scientist - Model trends and make predictions",
                    "Aerospace Engineer - Calculate rocket trajectories",
                    "Financial Analyst - Optimize profit and minimize costs"
                ],
                mini_project_ideas=[
                    "Analyze the trajectory of different sports balls using video",
                    "Design a parabolic solar cooker and test its efficiency",
                    "Create a profit optimization model for a small business",
                    "Build a model bridge with parabolic cables"
                ],
                difficulty_level="intermediate"
            )
        
        else:
            return RWALNarrative(
                topic_id=request.topic_id,
                student_mode=request.student_mode,
                title=f"Advanced Applications: {topic_name}",
                narrative="""Quadratic equations form the foundation of numerous advanced applications across 
                science and engineering. From quantum mechanics where probability amplitudes follow quadratic 
                relationships, to general relativity where spacetime curvature involves quadratic terms, 
                these equations are fundamental to our understanding of the universe. In optimization theory, 
                quadratic programming solves complex resource allocation problems.""",
                real_world_scenario="In particle physics, the trajectory of charged particles in electromagnetic "
                "fields follows parabolic paths. The Large Hadron Collider uses precise quadratic calculations "
                "to steer particles at near-light speeds. Understanding these equations is crucial for "
                "discovering new particles and understanding fundamental forces.",
                daily_life_examples=[
                    "GPS satellite orbit calculations",
                    "Stock market volatility modeling",
                    "Machine learning optimization algorithms",
                    "Acoustic design in concert halls",
                    "Lens design in cameras and telescopes"
                ],
                industry_applications=[
                    "Quantum Computing - Optimization algorithms",
                    "Machine Learning - Gradient descent and loss functions",
                    "Aerospace - Orbital mechanics and trajectory planning",
                    "Finance - Options pricing and risk modeling",
                    "Telecommunications - Signal processing and antenna design"
                ],
                career_connections=[
                    "Quantum Physicist - Research fundamental particles and forces",
                    "Machine Learning Engineer - Develop AI optimization algorithms",
                    "Quantitative Analyst - Model complex financial instruments",
                    "Aerospace Engineer - Design spacecraft trajectories",
                    "Research Scientist - Push the boundaries of human knowledge"
                ],
                mini_project_ideas=[
                    "Implement a quadratic programming solver from scratch",
                    "Model projectile motion with air resistance (differential equations)",
                    "Create a neural network and analyze its quadratic loss landscape",
                    "Design an optimal parabolic antenna for maximum signal gain",
                    "Simulate particle trajectories in electromagnetic fields"
                ],
                difficulty_level="advanced"
            )
    
    async def generate_quiz_questions(
        self,
        request: QuizQuestionRequest,
        topic_name: str,
        existing_questions: list[dict]
    ) -> list[GeneratedQuizQuestion]:
        logger.info(f"MockAIProvider: Generating {request.count} quiz questions for {request.topic_id}")
        
        questions = []
        for i in range(request.count):
            if request.student_mode == StudentMode.DULL:
                questions.append(GeneratedQuizQuestion(
                    question_text=f"If a ball is thrown and follows the path y = x² - 4, where does it land (cross the ground)?",
                    question_type="multiple_choice",
                    options=["x = 2 and x = -2", "x = 4 and x = -4", "x = 1 and x = -1", "x = 0"],
                    correct_answer="x = 2 and x = -2",
                    explanation="When the ball lands, y = 0. So x² - 4 = 0, which means x² = 4, so x = 2 or x = -2. The ball lands at two points!",
                    hint="Think about when the ball touches the ground - that's when y equals zero!",
                    bloom_level=request.bloom_level,
                    difficulty=request.difficulty
                ))
            elif request.student_mode == StudentMode.AVERAGE:
                questions.append(GeneratedQuizQuestion(
                    question_text=f"For the quadratic equation 2x² - 8x + 6 = 0, find the roots using the quadratic formula.",
                    question_type="multiple_choice",
                    options=["x = 1 and x = 3", "x = 2 and x = 3", "x = 1 and x = 2", "x = -1 and x = -3"],
                    correct_answer="x = 1 and x = 3",
                    explanation="Using x = (-b ± √(b²-4ac)) / 2a with a=2, b=-8, c=6: Discriminant = 64-48 = 16. x = (8 ± 4) / 4, giving x = 3 or x = 1.",
                    hint="First identify a, b, and c, then calculate the discriminant b² - 4ac.",
                    bloom_level=request.bloom_level,
                    difficulty=request.difficulty
                ))
            else:
                questions.append(GeneratedQuizQuestion(
                    question_text=f"Analyze the quadratic x² + 2x + 5 = 0. Express its roots in the form a + bi.",
                    question_type="short_answer",
                    options=None,
                    correct_answer="-1 + 2i and -1 - 2i",
                    explanation="Discriminant = 4 - 20 = -16 < 0, so roots are complex. x = (-2 ± √(-16)) / 2 = (-2 ± 4i) / 2 = -1 ± 2i",
                    hint="When the discriminant is negative, you'll get complex roots. Remember that √(-1) = i.",
                    bloom_level=request.bloom_level,
                    difficulty=request.difficulty
                ))
        
        return questions
    
    async def generate_worked_example(
        self,
        topic_id: str,
        problem: str,
        student_mode: StudentMode
    ) -> Dict[str, Any]:
        logger.info(f"MockAIProvider: Generating worked example for {topic_id}")
        
        if student_mode == StudentMode.DULL:
            return {
                "problem": problem or "Solve x² - 9 = 0",
                "steps": [
                    {"step": 1, "action": "Look at the equation", "explanation": "We have x² - 9 = 0. We need to find what x equals!", "visual_hint": "Think of x² as a mystery number times itself"},
                    {"step": 2, "action": "Move 9 to the other side", "explanation": "x² = 9. Now we know x times x equals 9!", "visual_hint": "What number times itself gives 9?"},
                    {"step": 3, "action": "Take the square root", "explanation": "x = √9 = ±3. Both 3×3=9 and (-3)×(-3)=9!", "visual_hint": "Don't forget the negative answer!"},
                    {"step": 4, "action": "Write the answer", "explanation": "x = 3 or x = -3. We found two answers!", "visual_hint": "Check: 3² - 9 = 0 ✓ and (-3)² - 9 = 0 ✓"}
                ],
                "final_answer": "x = 3 or x = -3",
                "real_world_connection": "If a square garden has an area of 9 square meters, each side is 3 meters long!"
            }
        elif student_mode == StudentMode.AVERAGE:
            return {
                "problem": problem or "Solve 2x² - 7x + 3 = 0 using the quadratic formula",
                "steps": [
                    {"step": 1, "action": "Identify coefficients", "explanation": "a = 2, b = -7, c = 3"},
                    {"step": 2, "action": "Calculate discriminant", "explanation": "Δ = b² - 4ac = (-7)² - 4(2)(3) = 49 - 24 = 25"},
                    {"step": 3, "action": "Apply quadratic formula", "explanation": "x = (-b ± √Δ) / 2a = (7 ± √25) / 4 = (7 ± 5) / 4"},
                    {"step": 4, "action": "Calculate both roots", "explanation": "x₁ = (7 + 5) / 4 = 3, x₂ = (7 - 5) / 4 = 0.5"}
                ],
                "final_answer": "x = 3 or x = 0.5",
                "verification": "Check: 2(3)² - 7(3) + 3 = 18 - 21 + 3 = 0 ✓"
            }
        else:
            return {
                "problem": problem or "Find the vertex form of y = 3x² - 12x + 7 and analyze its properties",
                "steps": [
                    {"step": 1, "action": "Factor out coefficient of x²", "explanation": "y = 3(x² - 4x) + 7"},
                    {"step": 2, "action": "Complete the square", "explanation": "y = 3(x² - 4x + 4 - 4) + 7 = 3((x-2)² - 4) + 7"},
                    {"step": 3, "action": "Simplify to vertex form", "explanation": "y = 3(x-2)² - 12 + 7 = 3(x-2)² - 5"},
                    {"step": 4, "action": "Identify vertex and properties", "explanation": "Vertex: (2, -5), Opens upward (a=3>0), Axis of symmetry: x=2"},
                    {"step": 5, "action": "Find roots using vertex form", "explanation": "0 = 3(x-2)² - 5 → (x-2)² = 5/3 → x = 2 ± √(5/3)"}
                ],
                "final_answer": "Vertex form: y = 3(x-2)² - 5, Vertex: (2, -5)",
                "advanced_analysis": {
                    "derivative": "dy/dx = 6x - 12, critical point at x = 2",
                    "concavity": "d²y/dx² = 6 > 0, always concave up",
                    "discriminant": "Δ = 144 - 84 = 60 > 0, two distinct real roots"
                }
            }
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text response for RAG and general queries (Mock implementation)."""
        logger.info(f"MockAIProvider: Generating text response (prompt length: {len(prompt)})")
        
        # Extract key information from the prompt to generate a contextual response
        prompt_lower = prompt.lower()
        
        # Check for question types and generate appropriate mock responses
        if "quadratic" in prompt_lower:
            if "solve" in prompt_lower or "root" in prompt_lower:
                return """To solve a quadratic equation ax² + bx + c = 0, you can use several methods:

1. **Factorization**: If the equation can be factored, write it as (px + q)(rx + s) = 0 and solve for x.

2. **Quadratic Formula**: x = (-b ± √(b² - 4ac)) / 2a
   - This works for all quadratic equations
   - The discriminant (b² - 4ac) tells us about the nature of roots

3. **Completing the Square**: Rewrite the equation in the form (x + p)² = q

The discriminant determines the nature of roots:
- If b² - 4ac > 0: Two distinct real roots
- If b² - 4ac = 0: One repeated real root
- If b² - 4ac < 0: Two complex conjugate roots

Remember to always check your answers by substituting back into the original equation!"""
            
            elif "graph" in prompt_lower or "parabola" in prompt_lower:
                return """A quadratic function y = ax² + bx + c produces a parabola when graphed:

**Key Features:**
1. **Vertex**: The turning point at x = -b/(2a), y = f(-b/(2a))
2. **Axis of Symmetry**: The vertical line x = -b/(2a)
3. **Direction**: Opens upward if a > 0, downward if a < 0
4. **Y-intercept**: The point (0, c)
5. **X-intercepts (roots)**: Where the parabola crosses the x-axis

**How coefficients affect the graph:**
- 'a' controls the width and direction (larger |a| = narrower parabola)
- 'b' shifts the vertex horizontally
- 'c' shifts the parabola vertically

Try adjusting the sliders in the visualization to see these effects in real-time!"""
            
            else:
                return """Quadratic equations are polynomial equations of degree 2, written in the standard form:

**ax² + bx + c = 0** (where a ≠ 0)

**Key Concepts:**
1. The coefficient 'a' determines if the parabola opens up or down
2. The discriminant (b² - 4ac) determines the nature of roots
3. The vertex form y = a(x-h)² + k shows the vertex at (h, k)

**Applications:**
- Projectile motion (ball trajectories)
- Area optimization problems
- Revenue and profit calculations
- Bridge and arch design

Quadratic equations appear everywhere in science and engineering!"""
        
        elif "discriminant" in prompt_lower:
            return """The discriminant is a key value in quadratic equations: **Δ = b² - 4ac**

**What it tells us:**
1. **Δ > 0**: Two distinct real roots
   - The parabola crosses the x-axis at two points
   
2. **Δ = 0**: One repeated real root (double root)
   - The parabola touches the x-axis at exactly one point (vertex)
   
3. **Δ < 0**: No real roots (two complex conjugate roots)
   - The parabola doesn't cross the x-axis
   - Roots are of the form: x = (-b ± i√|Δ|) / 2a

The discriminant is useful for quickly determining the nature of solutions without fully solving the equation."""
        
        else:
            # Generic educational response
            return """Based on the textbook content, here's what you need to know:

**Key Points:**
1. Mathematical concepts build upon each other - make sure you understand the fundamentals
2. Practice with different types of problems to strengthen your understanding
3. Real-world applications help connect abstract concepts to practical uses

**Study Tips:**
- Work through examples step by step
- Try to solve problems before looking at solutions
- Use visualizations to build intuition
- Connect new concepts to what you already know

If you have a specific question, feel free to ask for more detailed explanation!"""


class VertexAIProvider(AIProvider):
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self._client = None
        self._model = None
    
    async def _get_client(self):
        if self._client is None:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                
                vertexai.init(project=self.project_id, location=self.location)
                self._model = GenerativeModel("gemini-1.5-flash")
                self._client = True
                logger.info(f"VertexAI initialized with project {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize VertexAI: {e}")
                raise
        return self._model
    
    async def _generate_content(self, prompt: str) -> str:
        model = await self._get_client()
        response = await model.generate_content_async(prompt)
        return response.text
    
    async def generate_visual_config(
        self,
        topic_id: str,
        topic_name: str,
        learning_objectives: list[str],
        student_mode: StudentMode,
        mastery_level: float = 50.0
    ) -> VisualConfig:
        template = AIPromptTemplate.get_template_for_mode(student_mode)
        
        prompt = f"{template.system_prompt}\n\n{template.user_prompt_template.format(
            topic_name=topic_name,
            learning_objectives=', '.join(learning_objectives),
            mastery_level=mastery_level
        )}"
        
        try:
            response_text = await self._generate_content(prompt)
            json_str = response_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            config_dict = json.loads(json_str)
            config_dict["topic_id"] = topic_id
            config_dict["student_mode"] = student_mode
            
            return VisualConfig(**config_dict)
        except Exception as e:
            logger.error(f"VertexAI generation failed, falling back to mock: {e}")
            mock_provider = MockAIProvider()
            return await mock_provider.generate_visual_config(
                topic_id, topic_name, learning_objectives, student_mode, mastery_level
            )
    
    async def generate_rwal_narrative(
        self,
        request: RWALNarrativeRequest,
        topic_name: str,
        base_scenarios: list[dict]
    ) -> RWALNarrative:
        prompt = f"""Generate a real-world application narrative for teaching {topic_name} to a student 
        in {request.student_mode.value} learning mode.
        
        Base scenarios to build upon: {json.dumps(base_scenarios)}
        
        Return a JSON object with:
        - title: engaging title
        - narrative: 2-3 paragraph explanation
        - real_world_scenario: specific scenario description
        - daily_life_examples: list of 5 examples
        - industry_applications: list of 4 applications
        - career_connections: list of 4 careers
        - mini_project_ideas: list of 4 projects
        - difficulty_level: beginner/intermediate/advanced
        """
        
        try:
            response_text = await self._generate_content(prompt)
            json_str = response_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            narrative_dict = json.loads(json_str)
            narrative_dict["topic_id"] = request.topic_id
            narrative_dict["student_mode"] = request.student_mode
            
            return RWALNarrative(**narrative_dict)
        except Exception as e:
            logger.error(f"VertexAI RWAL generation failed, falling back to mock: {e}")
            mock_provider = MockAIProvider()
            return await mock_provider.generate_rwal_narrative(request, topic_name, base_scenarios)
    
    async def generate_quiz_questions(
        self,
        request: QuizQuestionRequest,
        topic_name: str,
        existing_questions: list[dict]
    ) -> list[GeneratedQuizQuestion]:
        prompt = f"""Generate {request.count} quiz question(s) for {topic_name} at Bloom's {request.bloom_level} level.
        
        Student mode: {request.student_mode.value}
        Difficulty: {request.difficulty}
        
        Existing questions to avoid duplicating: {json.dumps(existing_questions[:5])}
        
        Return a JSON array of objects, each with:
        - question_text: the question
        - question_type: multiple_choice or short_answer
        - options: list of 4 options (for multiple choice)
        - correct_answer: the correct answer
        - explanation: detailed explanation
        - hint: helpful hint
        - bloom_level: {request.bloom_level}
        - difficulty: {request.difficulty}
        """
        
        try:
            response_text = await self._generate_content(prompt)
            json_str = response_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            questions_list = json.loads(json_str)
            return [GeneratedQuizQuestion(**q) for q in questions_list]
        except Exception as e:
            logger.error(f"VertexAI quiz generation failed, falling back to mock: {e}")
            mock_provider = MockAIProvider()
            return await mock_provider.generate_quiz_questions(request, topic_name, existing_questions)
    
    async def generate_worked_example(
        self,
        topic_id: str,
        problem: str,
        student_mode: StudentMode
    ) -> Dict[str, Any]:
        prompt = f"""Generate a worked example for solving: {problem}
        
        Student mode: {student_mode.value}
        
        Return a JSON object with:
        - problem: the problem statement
        - steps: array of step objects with step number, action, explanation, and visual_hint
        - final_answer: the answer
        - real_world_connection: (for dull mode) or verification/advanced_analysis (for other modes)
        """
        
        try:
            response_text = await self._generate_content(prompt)
            json_str = response_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"VertexAI worked example generation failed, falling back to mock: {e}")
            mock_provider = MockAIProvider()
            return await mock_provider.generate_worked_example(topic_id, problem, student_mode)
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text response for RAG and general queries using Vertex AI."""
        try:
            response_text = await self._generate_content(prompt)
            return response_text
        except Exception as e:
            logger.error(f"VertexAI text generation failed, falling back to mock: {e}")
            mock_provider = MockAIProvider()
            return await mock_provider.generate_text(prompt, max_tokens)


def get_ai_provider() -> AIProvider:
    provider_type = os.getenv("AI_PROVIDER", "mock").lower()
    
    if provider_type == "vertex":
        project_id = os.getenv("VERTEX_AI_PROJECT")
        location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        
        if not project_id:
            logger.warning("VERTEX_AI_PROJECT not set, falling back to mock provider")
            return MockAIProvider()
        
        try:
            return VertexAIProvider(project_id, location)
        except Exception as e:
            logger.error(f"Failed to create VertexAI provider: {e}, falling back to mock")
            return MockAIProvider()
    
    return MockAIProvider()
