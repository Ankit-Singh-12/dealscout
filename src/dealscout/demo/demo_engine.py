import time
from typing import Iterator, List, Optional

from dealscout.framework.log_utils import (
    BG_BLACK,
    BG_BLUE,
    BLUE,
    CYAN,
    GREEN,
    MAGENTA,
    RED,
    RESET,
    WHITE,
    YELLOW,
)
from dealscout.demo.sample_deals import (
    CANDIDATE_OPPORTUNITIES,
    SEED_OPPORTUNITIES,
    DemoOpportunity,
)

# Pipeline stages the demo narrates and the UI renders as a stepper.
PIPELINE_STEPS = ["Scrape", "Summarize", "Price", "Rank", "Notify"]

# Surface a deal as an alert when the estimated saving clears this bar.
DEAL_THRESHOLD = 50.0

# How long to pause between narrated steps so the stream feels live.
STEP_DELAY = 0.55


def _agent_line(name: str, color: str, message: str) -> str:
    """Format a log line the same way the real agents do, so ``reformat`` styles it."""
    return f"{BG_BLACK}{color}[{name}] {message}{RESET}"


def _framework_line(message: str) -> str:
    return f"{BG_BLUE}{WHITE}[Agent Framework] {message}{RESET}"


class DemoProgress:
    """A single progress event streamed out of :meth:`DemoAgentFramework.run`."""

    def __init__(
        self,
        log: Optional[str] = None,
        step: Optional[int] = None,
        opportunity: Optional[DemoOpportunity] = None,
        notification: Optional[dict] = None,
        done: bool = False,
    ):
        self.log = log
        self.step = step
        self.opportunity = opportunity
        self.notification = notification
        self.done = done


class DemoAgentFramework:
    """Drop-in stand-in for ``DealAgentFramework`` used by the hosted demo."""

    PIPELINE_STEPS = PIPELINE_STEPS

    def __init__(self):
        # Start with a couple of tracked deals so the table is never empty.
        self.memory: List[DemoOpportunity] = list(SEED_OPPORTUNITIES)
        self.notifications: List[dict] = []
        self._cursor = 0
        self._sources = [
            "DealNews - Electronics",
            "DealNews - Computers",
            "DealNews - Smart Home",
            "DealNews - Home and Garden",
            "DealNews - Automotive",
        ]

    # -- helpers --------------------------------------------------------------

    def _next_batch(self, size: int = 4) -> List[DemoOpportunity]:
        """Rotate through the candidate pool so each run surfaces fresh deals."""
        if not CANDIDATE_OPPORTUNITIES:
            return []
        batch = []
        for offset in range(size):
            index = (self._cursor + offset) % len(CANDIDATE_OPPORTUNITIES)
            batch.append(CANDIDATE_OPPORTUNITIES[index])
        self._cursor = (self._cursor + size) % len(CANDIDATE_OPPORTUNITIES)
        return batch

    @staticmethod
    def build_notification(opportunity: DemoOpportunity) -> dict:
        """Shape a simulated push notification for an opportunity."""
        return {
            "title": opportunity.deal.title,
            "price": opportunity.deal.price,
            "estimate": opportunity.estimate,
            "discount": opportunity.discount,
            "discount_pct": opportunity.discount_pct,
            "url": opportunity.deal.url,
            "source": opportunity.deal.source,
            "time": time.strftime("%H:%M:%S"),
        }

    def _remember(self, opportunity: DemoOpportunity) -> bool:
        """Add an opportunity to memory unless we have already tracked that URL."""
        if any(item.deal.url == opportunity.deal.url for item in self.memory):
            return False
        self.memory.append(opportunity)
        return True

    # -- the narrated run -----------------------------------------------------

    def run(self) -> Iterator[DemoProgress]:
        """Narrate one full agentic cycle, yielding progress events as it goes."""
        batch = self._next_batch()

        # Step 1 - Scrape ------------------------------------------------------
        yield DemoProgress(
            log=_framework_line("Kicking off the Autonomous Planning Agent"), step=0
        )
        time.sleep(STEP_DELAY)
        yield DemoProgress(
            log=_agent_line(
                "Scanner Agent", CYAN, f"Scanning {len(self._sources)} live deal sources for bargains"
            ),
            step=0,
        )
        for source in self._sources:
            time.sleep(0.12)
            yield DemoProgress(log=_agent_line("Scanner Agent", CYAN, f"Fetched feed: {source}"), step=0)
        yield DemoProgress(
            log=_agent_line("Scanner Agent", CYAN, f"Collected {len(batch)} candidate deals to evaluate"),
            step=0,
        )

        # Step 2 - Summarize ---------------------------------------------------
        time.sleep(STEP_DELAY)
        for opportunity in batch:
            time.sleep(0.18)
            yield DemoProgress(
                log=_agent_line("Scanner Agent", CYAN, f"Summarized: {opportunity.deal.title}"),
                step=1,
            )

        # Step 3 - Price -------------------------------------------------------
        time.sleep(STEP_DELAY)
        yield DemoProgress(
            log=_agent_line("Ensemble Agent", YELLOW, "Pricing each deal with the model ensemble"),
            step=2,
        )
        priced: List[DemoOpportunity] = []
        for opportunity in batch:
            time.sleep(0.22)
            specialist = round(opportunity.estimate * 0.97, 2)
            frontier = round(opportunity.estimate * 1.02, 2)
            neural = round(opportunity.estimate * 0.99, 2)
            yield DemoProgress(
                log=_agent_line(
                    "Specialist Agent", RED, f"Fine-tuned model estimate: ${specialist:.2f}"
                ),
                step=2,
            )
            yield DemoProgress(
                log=_agent_line("Frontier Agent", BLUE, f"RAG estimate: ${frontier:.2f}"),
                step=2,
            )
            yield DemoProgress(
                log=_agent_line(
                    "Neural Network Agent", MAGENTA, f"Deep model estimate: ${neural:.2f}"
                ),
                step=2,
            )
            yield DemoProgress(
                log=_agent_line(
                    "Ensemble Agent",
                    YELLOW,
                    f"{opportunity.deal.title} -> est. ${opportunity.estimate:.2f} "
                    f"(deal ${opportunity.deal.price:.2f})",
                ),
                step=2,
                opportunity=opportunity,
            )
            priced.append(opportunity)

        # Step 4 - Rank --------------------------------------------------------
        time.sleep(STEP_DELAY)
        priced.sort(key=lambda item: item.discount, reverse=True)
        best = priced[0] if priced else None
        for opportunity in priced:
            self._remember(opportunity)
        if best:
            yield DemoProgress(
                log=_agent_line(
                    "Planning Agent",
                    GREEN,
                    f"Best opportunity: {best.deal.title} saves ${best.discount:.2f} "
                    f"({best.discount_pct:.0f}%)",
                ),
                step=3,
            )

        # Step 5 - Notify ------------------------------------------------------
        time.sleep(STEP_DELAY)
        notification = None
        if best and best.discount > DEAL_THRESHOLD:
            yield DemoProgress(
                log=_agent_line("Messaging Agent", WHITE, "Crafting a push notification for the best deal"),
                step=4,
            )
            time.sleep(0.25)
            notification = self.build_notification(best)
            self.notifications.insert(0, notification)
            yield DemoProgress(
                log=_agent_line("Messaging Agent", WHITE, "Push notification sent to the user"),
                step=4,
                notification=notification,
            )
        else:
            yield DemoProgress(
                log=_agent_line("Planning Agent", GREEN, "No deal cleared the savings threshold this cycle"),
                step=4,
            )

        yield DemoProgress(
            log=_framework_line("Planning Agent run complete"), step=4, done=True
        )

    def alert(self, opportunity: DemoOpportunity) -> dict:
        """Simulate sending a push notification for a chosen opportunity."""
        notification = self.build_notification(opportunity)
        self.notifications.insert(0, notification)
        return notification