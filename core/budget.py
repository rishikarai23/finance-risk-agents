from datetime import datetime

class TokenBudget:
    def __init__(self,max_tokens: int = 50000):
        self.max_tokens = max_tokens
        self.used_tokens = 0
        self.agent_breakdown: dict[str , int] = {}
        # so an example could be news_agent , 5000
        self.created_at = datetime.now().isoformat()

    def consume(self,agent_name: str,tokens: int) -> None :
        """Called after every agent run to record token usage."""
        self.used_tokens += tokens
        if agent_name in self.agent_breakdown:
            self.agent_breakdown[agent_name] += tokens
        else:
            self.agent_breakdown[agent_name] = tokens

    def remaining(self):
        """How many tokens remain after using a certain number"""
        return self.max_tokens - self.used_tokens
    
    def can_proceed(self , estimated_tokens: int = 2000):
        """So we need atleast 2000 tokens remaining for the agent to continue working"""
        return self.remaining()>=estimated_tokens
    
    def summary(self) -> dict:
        """Total breakdown of the agent"""
        return {
            "max_tokens" : self.max_tokens,
            "used_tokens" : self.used_tokens,
            "remaining_tokens" : self.remaining(),
            "percentage used" : round((self.used_tokens / self.max_tokens)*100,2),
            "agent_breakdown" : self.agent_breakdown
        }