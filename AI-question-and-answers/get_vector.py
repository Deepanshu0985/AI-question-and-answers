from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
import time
import datetime
import traceback
from data_cleaning import extract_subject_data
from final_json import apply_set_mappings
from vector_clean import merge_models



LOG_FILE = "app.log"  # path to log file

def log(message, level="INFO"):
    """Pretty colored console logger with timestamps and file saving."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "INFO": "\033[94m",      # Blue
        "SUCCESS": "\033[92m",   # Green
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
    }
    reset = "\033[0m"
    color = colors.get(level, "")

    log_line = f"[{timestamp}] [{level}] {message}"

    print(f"{color}{log_line}{reset}")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def log_error(e, context=""):
    """Log error with traceback."""
    error_message = f"Error in {context}: {e}"
    log(error_message, "ERROR")

    tb = traceback.format_exc()
    print(tb)  
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(tb + "\n")
# ==============================
# MODEL SETUP
# ==============================

model1 = ChatOllama(model="phi4:latest", temperature=0)
model6 = ChatOllama(model="gpt-oss:20b", temperature=0)
models = [model1, model6]


# ==============================
# PROMPT TEMPLATE
# ==============================

accurate_prompt = strict_prompt = ChatPromptTemplate.from_template("""
SYSTEM:
You are a classification assistant. You MUST output ONLY a single valid JSON object and NOTHING else.
Use only the exact category names listed below (exact spelling). Do not invent or alter category names.

Categories:
{topics}

RULES (must follow exactly):
1) Output only ONE valid JSON object. No explanations, no extra text, no backticks.
2) Use ONLY keys from the categories above (exact spellings).
3) Numeric values must be integers and sum exactly to 100 (e.g., 100, 50, 25).
4) If a question clearly belongs to a single category, assign 100 to that category.
5) If a question involves multiple topics, divide the percentages according to the **relevance or weightage** of each topic. Ensure the sum is exactly 100.
6) classify based on the answer, not just the question and if you cannot solve skip the question.
7) properly read and understand the question and answer before classifying.
8) only add non zero results to the JSON object.

EXAMPLES OF VALID OUTPUT:

# Single-topic question:
{{"Alkenes": 100}}

# Multi-topic question:
{{"Reaction Mechanisms": 70, "Optical Isomerism": 30}}

# Another multi-topic example:
{{"Coordination compounds": 60, "Chemical Bonding": 40}}

QUESTION: {questions}



OUTPUT (ONLY the valid JSON object):
""")


# ==============================
# CLASSIFICATION FUNCTION
# ==============================

def get_topic_vector(question, topic_string, model):
    try:
        chain = accurate_prompt | model
        response = chain.invoke({"questions": question, "topics": topic_string})
        text = response.content.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No valid JSON found")

        data = json.loads(text[start:end])
        log(f"✅ Successfully classified question: {question[:70]}...", "SUCCESS")
        return data

    except Exception as e:
        log_error(e, context=f"get_topic_vector() | Question: {question[:70]}")
        return {"Error": 100.0}


# ==============================
# MAIN FUNCTION
# ==============================

def extractJson(Physics, Chemistry, Maths,mapping_file):
    physics_topics = ["Vectors","Types of Forces","Newton’s Laws of Motion","Friction","Basics of calculus",
                      "1 D Kinematics","2 D Kinematics","Circular Motion","Work, Power and Energy",
                      "Center of Mass","Conservation of Momentum","Rotation","Fluid Statics and Dynamics",
                      "Properties of Solids","Surface Tension and Viscosity","Simple Harmonic Motion",
                      "Combination of SHM","Damping and Resonance","Waves on a string","Sound Waves",
                      "Light Waves and Interference","Ray Optics","Thermal Expansion and Calorimetry",
                      "Kinetic Theory of Gases","1st Law of Thermodynamics & specific heats","Heat transfer",
                      "Electrostatics","Dielectrics and Capacitors","Current Electricity","Magnetism",
                      "Electromagnetic Induction","Alternating Current","Modern Physics","Gravitation"]

    maths_topics = ["Number System", "Factors and Indices","Sets","Progressions and Series",
                    "Quadratic Equations & Theory of Equations","Logarithms","Trigonometric Identities and Equations",
                    "Determinants and Matrices","Straight Lines and Pair of Lines","Circles","Permutations and Combinations",
                    "Binomial Theorem","Complex Numbers","Solution of Triangles","Functions","Inverse Trigonometry",
                    "Limits and Continuity","Derivatives and Method of Differentiation","Application of Derivatives",
                    "Indefinite Integration","Definite Integration","Area Under the Curves","Differential Equations",
                    "Vectors and 3D Geometry","Probability","Parabola","Ellipse","Hyperbola"]

    chemistry_topics = ["Periodic Table","Chemical Bonding","Atomic Structure","Mole Concept","Gaseous State",
                        "Thermodynamics","Thermochemistry","Chemical Equilibrium","Ionic Equilibrium","Redox Reactions",
                        "s-block Elements","Hydrogen and Related Compounds","Nomenclature","Solid State","Boron Family",
                        "Structural and Geometrical Isomerism","Liquid Solutions and Colligative Properties",
                        "Chemical Kinetics","Surface Chemistry","Carbon Family","Metallurgy","d-block elements",
                        "f-block elements","General Organic Chemistry","Electrochemistry","Reaction Mechanisms",
                        "Tautomerism","Optical Isomerism","Alkanes","Alkenes","Alkynes","Arenes","Alkyl and Aryl Halides",
                        "Alcohols, Phenols and Ethers","Aldehydes and Ketones","Nitrogen Family","Amines",
                        "Carboxylic Acid and Derivatives","Qualitative Analysis","Coordination compounds",
                        "Biomolecules and Polymers","16, 17 and 18 family","Practical Organic Chemistry"]

    subject = [Physics, Chemistry, Maths]
    print(Physics)
    print(len(Physics))
    topic = [physics_topics, chemistry_topics, maths_topics]
    subject_names = ["physics", "chemistry", "maths"]
    result = {}

    for model in models:
        model_name = getattr(model, 'model', str(model)).split(":")[0]
        log(f"🔹 Using model: {model_name}", "INFO")

        result[model_name] = {}

        for i, subject_set in enumerate(subject):
            all_results = []
            subject_name = subject_names[i]
            log(f"📘 Processing subject: {subject_name}...", "INFO")

            for j, q in enumerate(subject_set):
                log(f"➡️ Processing question {j+1}/{len(subject_set)}", "INFO")

                if j % 10 == 0 and j != 0:
                    log("⏳ Pausing 2 seconds to avoid rate limit...", "WARNING")
                    time.sleep(2)

                topic_data = get_topic_vector(q, topic[i], model)
                all_results.append({
                    "question_id": j + 1,
                    "question": q,
                    "topic_vector": topic_data
                })
                log(f"✔️ Finished question {j+1}: {topic_data}", "SUCCESS")

            result[model_name][subject_name] = all_results
            log(f"✅ Completed subject: {subject_name}", "SUCCESS")

    log("🎯 All models and subjects processed successfully!", "SUCCESS")
    print("Final Result:", result)
   
    mapping = extract_subject_data(mapping_file)
    print("Mapping DataFrames extracted.")
    print(mapping)
    result = merge_models(result)
    print("Models merged.")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    result = apply_set_mappings(result, mapping)
    result =  json.dumps(result, ensure_ascii=False,indent =2)
    
    
    return result


# ==============================
# RUN
# ==============================

# if __name__ == "__main__":
#     log(" Starting classification process...", "INFO")
#     results = extractJson(Physics, Chemistry, Maths)
#     log(" Process completed.", "SUCCESS")
#     print(results)