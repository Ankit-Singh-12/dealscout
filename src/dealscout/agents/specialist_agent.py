import modal
from dealscout.agents.agent import Agent


class SpecialistAgent(Agent):
    """
    An Agent that runs our fine-tuned LLM that's running remotely on Modal
    """

    name = "Specialist Agent"
    color = Agent.RED

    def __init__(self):
        """
        Set up this Agent by creating an instance of the modal class
        """
        self.log("Specialist Agent is initializing - connecting to modal")
        DealScout = modal.Cls.from_name("dealscout-service", "DealScout")
        self.deal_scout = DealScout()

    def price(self, description: str) -> float:
        """
        Make a remote call to return the estimate of the price of this item
        """
        self.log("Specialist Agent is calling remote fine-tuned model")
        result = self.deal_scout.price.remote(description)
        self.log(f"Specialist Agent completed - predicting ${result:.2f}")
        return result
    