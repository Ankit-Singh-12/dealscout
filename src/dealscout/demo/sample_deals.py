from typing import List
from pydantic import BaseModel


class DemoDeal(BaseModel):
    """A single scraped product, enriched with fields the demo UI shows."""

    title: str
    product_description: str
    price: float
    url: str
    category: str
    source: str
    image: str = ""


class DemoOpportunity(BaseModel):
    """A priced deal: what we paid vs. what the ensemble thinks it is worth."""

    deal: DemoDeal
    estimate: float
    discount: float

    @property
    def discount_pct(self) -> float:
        if self.estimate <= 0:
            return 0.0
        return round((self.discount / self.estimate) * 100, 1)


def _opp(
    title: str,
    description: str,
    price: float,
    estimate: float,
    url: str,
    category: str,
    source: str,
    image: str = "",
) -> DemoOpportunity:
    """Build an opportunity, deriving the discount so it always stays consistent."""
    deal = DemoDeal(
        title=title,
        product_description=description,
        price=price,
        url=url,
        category=category,
        source=source,
        image=image,
    )
    return DemoOpportunity(deal=deal, estimate=estimate, discount=round(estimate - price, 2))


# Deals that are "already tracked" when the dashboard first loads, so the demo
# never opens on an empty table.
SEED_OPPORTUNITIES: List[DemoOpportunity] = [
    _opp(
        title="Apple Watch SE (2nd Gen) GPS 40mm",
        description="The Apple Watch SE (2nd Gen) features a 40mm aluminum case with an always-bright Retina display and the S8 chip for snappy performance. It tracks workouts, heart rate, sleep and blood oxygen trends, and includes crash and fall detection for added safety. Water resistant to 50 meters, it pairs with iPhone for notifications, Apple Pay and turn-by-turn directions.",
        price=199.00,
        estimate=279.00,
        url="https://www.dealnews.com/products/Apple/Apple-Watch-SE-2-nd-Gen-GPS-40-mm/421268.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title="Samsung 980 1TB PCIe NVMe SSD",
        description="The Samsung 980 is a 1TB PCIe 3.0 NVMe M.2 solid state drive built for fast boot times and quick file transfers. It delivers sequential read speeds up to 3,500 MB/s using Samsung's in-house controller and intelligent TurboWrite caching. Ideal as a boot drive or game library upgrade for desktops and compatible laptops.",
        price=59.00,
        estimate=99.00,
        url="https://www.dealnews.com/products/Samsung/Samsung-980-1-TB-PCIe-NVMe-SSD/385012.html",
        category="Computers",
        source="DealNews - Computers",
    ),
]


# The pool of deals the simulated scanner "discovers" on each run.
CANDIDATE_OPPORTUNITIES: List[DemoOpportunity] = [
    _opp(
        title='Hisense 55" R6 Series 4K UHD Roku Smart TV',
        description="The Hisense 55-inch R6 Series is a 4K UHD smart TV with 3840x2160 resolution and Dolby Vision HDR for vivid contrast and color. It runs the Roku TV platform with thousands of streaming channels and hands-free voice control via Alexa and Google Assistant. Three HDMI inputs make it easy to connect game consoles, soundbars and streaming devices.",
        price=178.00,
        estimate=298.00,
        url="https://www.dealnews.com/products/Hisense/Hisense-R6-Series-55-R6030-N-55-4-K-UHD-Roku-Smart-TV/484824.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title="Apple AirPods Pro (2nd Gen) USB-C",
        description="The 2nd-generation Apple AirPods Pro deliver up to 2x more active noise cancellation than the prior model, plus Adaptive Audio that blends transparency and ANC on the fly. The USB-C charging case adds a speaker, lanyard loop and precision Find My tracking. Personalized Spatial Audio and a low-distortion driver give clear, immersive sound for music and calls.",
        price=169.00,
        estimate=249.00,
        url="https://www.dealnews.com/products/Apple/Apple-Air-Pods-Pro-2-nd-Gen-USB-C/472901.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title='Lenovo IdeaPad Slim 5 16" Ryzen 5 Laptop',
        description="The Lenovo IdeaPad Slim 5 pairs a 7th-gen AMD Ryzen 5 8645HS 6-core CPU with 16GB of RAM and a 512GB SSD for responsive everyday multitasking. Its 16-inch 1920x1200 touch display is bright and roomy for spreadsheets, browsing and media. A sturdy aluminum lid, fast charging and a full-size keyboard round out a capable mainstream notebook.",
        price=446.00,
        estimate=640.00,
        url="https://www.dealnews.com/products/Lenovo/Lenovo-Idea-Pad-Slim-5-16-Touch-Laptop/485068.html",
        category="Computers",
        source="DealNews - Computers",
    ),
    _opp(
        title="Dell G15 Ryzen 5 Gaming Laptop w/ RTX 3050",
        description="The Dell G15 gaming laptop runs an AMD Ryzen 5 7640HS 6-core CPU alongside an NVIDIA GeForce RTX 3050 GPU for smooth 1080p gaming. Its 15.6-inch 120Hz display keeps fast-paced action crisp, while 16GB of RAM and a 1TB NVMe SSD handle modern titles and quick load times. Dual-fan cooling and a game-ready keyboard make it a strong budget gaming pick.",
        price=650.00,
        estimate=879.00,
        url="https://www.dealnews.com/products/Dell/Dell-G15-Ryzen-5-15-6-Gaming-Laptop-w-Nvidia-RTX-3050/485067.html",
        category="Computers",
        source="DealNews - Computers",
    ),
    _opp(
        title="Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
        description="The Sony WH-1000XM5 are over-ear wireless headphones with eight microphones and two processors driving best-in-class adaptive noise cancellation. They deliver up to 30 hours of battery life, quick charging, and crystal-clear hands-free calling with precise voice pickup. Lightweight memory-foam earcups and multipoint Bluetooth make all-day listening comfortable across devices.",
        price=298.00,
        estimate=399.00,
        url="https://www.dealnews.com/products/Sony/Sony-WH-1000-XM5-Wireless-Headphones/472233.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title="Ninja AF101 Air Fryer 4-qt",
        description="The Ninja AF101 is a 4-quart air fryer that crisps, roasts, reheats and dehydrates with up to 75% less added fat than traditional frying. A wide 105F to 400F temperature range gives precise control, and the nonstick basket and crisper plate are dishwasher safe for easy cleanup. Its compact footprint suits smaller kitchens while still cooking for two to four people.",
        price=79.00,
        estimate=129.00,
        url="https://www.dealnews.com/products/Ninja/Ninja-AF101-Air-Fryer/1135993.html",
        category="Home and Garden",
        source="DealNews - Home and Garden",
    ),
    _opp(
        title="Samsung 990 Pro 2TB PCIe 4.0 NVMe SSD",
        description="The Samsung 990 Pro is a 2TB PCIe 4.0 NVMe M.2 drive engineered for enthusiasts, hitting sequential reads up to 7,450 MB/s. Improved power efficiency and a nickel-coated controller keep thermals in check during sustained workloads. It is an excellent upgrade for PS5 storage, content creation and high-end gaming rigs.",
        price=149.00,
        estimate=219.00,
        url="https://www.dealnews.com/products/Samsung/Samsung-990-Pro-2-TB-PCIe-4-0-NVMe-SSD/479551.html",
        category="Computers",
        source="DealNews - Computers",
    ),
    _opp(
        title="iRobot Roomba j7+ Self-Emptying Robot Vacuum",
        description="The iRobot Roomba j7+ is a self-emptying robot vacuum that uses front-facing PrecisionVision navigation to avoid cords, charging cables and pet waste. Its Clean Base automatically empties debris into a bag that holds up to 60 days of dirt. Smart mapping lets you target specific rooms by voice or app, and it learns your cleaning habits over time.",
        price=399.00,
        estimate=599.00,
        url="https://www.dealnews.com/products/i-Robot/i-Robot-Roomba-j7-Self-Emptying-Robot-Vacuum/440197.html",
        category="Smart Home",
        source="DealNews - Smart Home",
    ),
    _opp(
        title='LG 27" UltraGear QHD 165Hz Gaming Monitor',
        description="The LG 27GP750 UltraGear is a 27-inch QHD 2560x1440 gaming monitor with a fast 165Hz refresh rate and 1ms response time. NVIDIA G-Sync and AMD FreeSync Premium compatibility keep gameplay tear-free, while HDR10 adds punch to highlights. A nearly borderless IPS panel delivers wide viewing angles and accurate color for both gaming and creative work.",
        price=196.00,
        estimate=299.00,
        url="https://www.dealnews.com/products/LG/LG-Ultra-Gear-27-GP750-27-1440-p-165-Hz-Gaming-Monitor/479882.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title="Anker 737 Power Bank 24,000mAh 140W",
        description="The Anker 737 is a 24,000mAh power bank that pushes up to 140W over USB-C, enough to fast-charge many laptops as well as phones and tablets. A smart digital display shows remaining capacity, input/output wattage and time to full. Three ports let you top up multiple devices at once, making it a strong travel and work-from-anywhere companion.",
        price=89.00,
        estimate=149.00,
        url="https://www.dealnews.com/products/Anker/Anker-737-Power-Bank-24-000-m-Ah/461920.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
    _opp(
        title="Google Nest Learning Thermostat (3rd Gen)",
        description="The 3rd-gen Nest Learning Thermostat programs itself by learning the temperatures you like and building a schedule around your routine. Its Farsight display shows the time or temperature from across the room, and Auto-Eco mode trims energy use when you are away. Remote control from the Home app and Energy History reports help lower heating and cooling bills.",
        price=169.00,
        estimate=249.00,
        url="https://www.dealnews.com/products/Google/Google-Nest-Learning-Thermostat-3-rd-Gen/130103.html",
        category="Smart Home",
        source="DealNews - Smart Home",
    ),
    _opp(
        title="Bose SoundLink Flex Portable Bluetooth Speaker",
        description="The Bose SoundLink Flex is a rugged portable Bluetooth speaker tuned with PositionIQ to optimize sound however it is placed. It is IP67 rated against water and dust, floats, and survives drops, making it ideal for trips and the outdoors. Up to 12 hours of battery and a built-in mic for calls keep it useful well beyond music.",
        price=99.00,
        estimate=149.00,
        url="https://www.dealnews.com/products/Bose/Bose-Sound-Link-Flex-Portable-Bluetooth-Speaker/459031.html",
        category="Electronics",
        source="DealNews - Electronics",
    ),
]