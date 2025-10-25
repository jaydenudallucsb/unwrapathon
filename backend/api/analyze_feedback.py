import pandas as pd
import json
import asyncio
from pydantic import BaseModel, Field
from typing import Dict, Any
from your_openai_file import create_openai_completion, GPT5Deployment, ReasoningEffort

class AnalyzeFeedbackTool(BaseModel):
    """Cluster feedback by group and theme for bubble visualization."""
    csv_path: str = Field(..., description="Path to feedback CSV")

    async def execute(self) -> Dict[str, Any]:
        df = pd.read_csv(self.csv_path)
        
        # Step 1: Basic cleaning
        df = df.dropna(subset=['Entry Text'])
        df = df.fillna("")
        
        # Step 2: Group by 'Groups' to get aggregate chunks
        group_data = {}
        for group_name, group_df in df.groupby('Groups'):
            sample_texts = "\n".join(group_df['Entry Text'].head(30).tolist())
            avg_sent = group_df['Sentiment'].astype(str).value_counts(normalize=True).to_dict()
            group_data[group_name] = {"text": sample_texts, "sentiment_distribution": avg_sent}

        # Step 3: Ask GPT to find sub-themes per group
        prompt = f"""
        You are an analytics assistant for customer feedback like Unwrap.ai.
        Given grouped user feedback, identify sub-themes, average sentiment (-1 to +1),
        and the number of mentions for each sub-theme.

        Return a JSON list in this format:
        [
          {{
            "group": "Checkout",
            "theme": "Payment flow",
            "sentiment": 0.7,
            "mentions": 20,
            "representative_quote": "Loved the new checkout experience!"
          }},
          ...
        ]

        Feedback groups:
        {json.dumps(group_data, indent=2)}
        """

        response = await create_openai_completion(
            messages=[{"role": "user", "content": prompt}],
            model=GPT5Deployment.GPT_5_MINI,
            reasoning_effort=ReasoningEffort.LOW,
        )

        raw = response.choices[0].message.content
        try:
            clusters = json.loads(raw)
        except json.JSONDecodeError:
            clusters = {"error": "Invalid JSON from model", "raw": raw}
        
        return clusters