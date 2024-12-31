from langchain_openai import AzureChatOpenAI

from dotenv import load_dotenv
load_dotenv()
# OpenAI 모델 초기화
llm = AzureChatOpenAI(model="gpt-4o", temperature=0)  

# 간단한 JSON Schema 정의
json_schema = {
    "title": "SimplePlan",  # Title 추가
    "description": "A simple structured output schema for a goal and steps to achieve it.",  # Description 추가
    "type": "object",
    "properties": {
        "goal": {
            "type": "string",
            "description": "The main goal the user wants to achieve"
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "Step-by-step actions to achieve the goal"
            },
            "description": "A list of steps to accomplish the goal"
        }
    },
    "required": ["goal", "steps"]
}

# 모델에 JSON Schema를 사용한 출력 파서 추가
structured_model = llm.with_structured_output(json_schema)

# 테스트 질문
query = "I want to get fit. Suggest a goal and steps to achieve it."

# 모델 실행
output = structured_model.invoke(query)

# 출력 확인
print("Structured Output:")
print(output)