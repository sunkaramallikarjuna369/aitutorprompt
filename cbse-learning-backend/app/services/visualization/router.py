from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import math

router = APIRouter(prefix="/visualization", tags=["Visualization"])

class QuadraticInput(BaseModel):
    a: float = Field(..., description="Coefficient of x²")
    b: float = Field(..., description="Coefficient of x")
    c: float = Field(..., description="Constant term")

class QuadraticAnalysis(BaseModel):
    a: float
    b: float
    c: float
    discriminant: float
    discriminant_interpretation: str
    roots: Optional[List[float]]
    roots_type: str
    vertex: Tuple[float, float]
    axis_of_symmetry: float
    direction: str
    y_intercept: float
    plot_points: List[Tuple[float, float]]
    equation_string: str
    factored_form: Optional[str]
    vertex_form: str

class PlotRequest(BaseModel):
    a: float
    b: float
    c: float
    x_min: float = -10
    x_max: float = 10
    num_points: int = 50

@router.post("/quadratic/analyze", response_model=QuadraticAnalysis)
async def analyze_quadratic(input_data: QuadraticInput):
    a, b, c = input_data.a, input_data.b, input_data.c
    
    if a == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coefficient 'a' cannot be zero for a quadratic equation"
        )
    
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        roots = sorted([round(root1, 4), round(root2, 4)])
        roots_type = "two_distinct_real"
        discriminant_interpretation = "D > 0: Two distinct real roots"
    elif discriminant == 0:
        root = -b / (2*a)
        roots = [round(root, 4)]
        roots_type = "two_equal_real"
        discriminant_interpretation = "D = 0: Two equal real roots (repeated root)"
    else:
        roots = None
        roots_type = "no_real_roots"
        discriminant_interpretation = "D < 0: No real roots (complex roots)"
    
    vertex_x = -b / (2*a)
    vertex_y = a * vertex_x**2 + b * vertex_x + c
    vertex = (round(vertex_x, 4), round(vertex_y, 4))
    
    axis_of_symmetry = round(vertex_x, 4)
    
    direction = "upward" if a > 0 else "downward"
    
    y_intercept = c
    
    x_range = 10
    if roots:
        x_range = max(abs(r) for r in roots) + 5
    x_range = max(x_range, abs(vertex_x) + 5)
    
    plot_points = []
    for i in range(51):
        x = -x_range + (2 * x_range * i / 50)
        y = a * x**2 + b * x + c
        plot_points.append((round(x, 2), round(y, 2)))
    
    def format_coef(coef, var, first=False):
        if coef == 0:
            return ""
        sign = "" if first else ("+" if coef > 0 else "")
        if abs(coef) == 1 and var:
            return f"{sign}{'-' if coef < 0 else ''}{var}"
        return f"{sign}{coef}{var}"
    
    equation_parts = []
    if a != 0:
        equation_parts.append(format_coef(a, "x²", True))
    if b != 0:
        equation_parts.append(format_coef(b, "x", len(equation_parts) == 0))
    if c != 0:
        equation_parts.append(format_coef(c, "", len(equation_parts) == 0))
    equation_string = " ".join(equation_parts) + " = 0" if equation_parts else "0 = 0"
    
    factored_form = None
    if roots and len(roots) == 2:
        r1, r2 = roots
        if a == 1:
            factored_form = f"(x - {r1})(x - {r2}) = 0"
        else:
            factored_form = f"{a}(x - {r1})(x - {r2}) = 0"
    elif roots and len(roots) == 1:
        r = roots[0]
        if a == 1:
            factored_form = f"(x - {r})² = 0"
        else:
            factored_form = f"{a}(x - {r})² = 0"
    
    h, k = vertex
    if a == 1:
        vertex_form = f"(x - {h})² + {k}" if k >= 0 else f"(x - {h})² - {abs(k)}"
    else:
        vertex_form = f"{a}(x - {h})² + {k}" if k >= 0 else f"{a}(x - {h})² - {abs(k)}"
    
    return QuadraticAnalysis(
        a=a,
        b=b,
        c=c,
        discriminant=round(discriminant, 4),
        discriminant_interpretation=discriminant_interpretation,
        roots=roots,
        roots_type=roots_type,
        vertex=vertex,
        axis_of_symmetry=axis_of_symmetry,
        direction=direction,
        y_intercept=y_intercept,
        plot_points=plot_points,
        equation_string=equation_string,
        factored_form=factored_form,
        vertex_form=vertex_form
    )

@router.post("/quadratic/plot-points")
async def get_plot_points(request: PlotRequest):
    a, b, c = request.a, request.b, request.c
    
    if a == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coefficient 'a' cannot be zero for a quadratic equation"
        )
    
    points = []
    step = (request.x_max - request.x_min) / (request.num_points - 1)
    
    for i in range(request.num_points):
        x = request.x_min + i * step
        y = a * x**2 + b * x + c
        points.append({"x": round(x, 4), "y": round(y, 4)})
    
    return {"points": points, "equation": f"{a}x² + {b}x + {c}"}

@router.post("/quadratic/solve-steps")
async def get_solution_steps(input_data: QuadraticInput):
    a, b, c = input_data.a, input_data.b, input_data.c
    
    if a == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coefficient 'a' cannot be zero"
        )
    
    steps = []
    
    steps.append({
        "step": 1,
        "title": "Identify coefficients",
        "content": f"From {a}x² + {b}x + {c} = 0:\na = {a}, b = {b}, c = {c}"
    })
    
    discriminant = b**2 - 4*a*c
    steps.append({
        "step": 2,
        "title": "Calculate discriminant",
        "content": f"D = b² - 4ac = ({b})² - 4({a})({c}) = {b**2} - {4*a*c} = {discriminant}"
    })
    
    if discriminant > 0:
        sqrt_d = math.sqrt(discriminant)
        root1 = (-b + sqrt_d) / (2*a)
        root2 = (-b - sqrt_d) / (2*a)
        steps.append({
            "step": 3,
            "title": "Apply quadratic formula",
            "content": f"Since D > 0, we have two distinct real roots.\nx = (-b ± √D) / 2a\nx = ({-b} ± √{discriminant}) / {2*a}\nx = ({-b} ± {sqrt_d:.4f}) / {2*a}"
        })
        steps.append({
            "step": 4,
            "title": "Calculate roots",
            "content": f"x₁ = ({-b} + {sqrt_d:.4f}) / {2*a} = {root1:.4f}\nx₂ = ({-b} - {sqrt_d:.4f}) / {2*a} = {root2:.4f}"
        })
    elif discriminant == 0:
        root = -b / (2*a)
        steps.append({
            "step": 3,
            "title": "Apply quadratic formula",
            "content": f"Since D = 0, we have two equal real roots.\nx = -b / 2a = {-b} / {2*a} = {root:.4f}"
        })
    else:
        steps.append({
            "step": 3,
            "title": "Interpret discriminant",
            "content": f"Since D < 0 (D = {discriminant}), the equation has no real roots.\nThe roots are complex numbers."
        })
    
    return {"steps": steps, "discriminant": discriminant}

@router.get("/configs/{config_id}")
async def get_visualization_config(config_id: str):
    from ...utils.database import db
    config = db.get_visual_config(config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visualization config {config_id} not found"
        )
    return config
