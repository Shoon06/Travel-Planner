# C:\Users\ASUS\MyanmarTravelPlanner\populate_rich_destination_content.py

import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

RICH_CONTENT = {
    'Heho': {
        'history': """
            <div class="history-content">
                <p>Heho is a small town in Shan State, Myanmar, best known as the gateway to the famous Inle Lake. Originally a sleepy farming village, Heho grew in importance when an airfield was constructed by the British during World War II.</p>
                
                <p>The town sits at an elevation of 3,850 feet (1,173 meters) in the Shan Highlands, surrounded by rolling hills and farmland. After Burma's independence, Heho Airport became the primary access point for visitors heading to Inle Lake, transforming the town into a transportation hub.</p>
                
                <p>Today, Heho maintains its small-town charm while serving thousands of tourists annually. The surrounding area is home to ethnic Pa-O, Shan, and Danu communities, each contributing to the region's rich cultural tapestry.</p>
                
                <div class="history-highlight mt-3 p-3 bg-light rounded">
                    <i class="fas fa-plane text-primary me-2"></i>
                    <strong>Key Fact:</strong> Heho's airport was originally built by the British in the 1940s and was used as a military airfield during WWII.
                </div>
            </div>
        """,
        
        'attractions': """
            <div class="attractions-grid">
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-water text-info fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Nearby Inle Lake</h5>
                            <p class="text-gray">Freshwater lake famous for leg-rowing fishermen and floating villages. Just a 45-minute drive from Heho.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-mountain text-success fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Pindaya Caves</h5>
                            <p class="text-gray">Limestone caves containing over 8,000 Buddha images. Located about 2 hours from Heho.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-pagoda text-warning fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Kakku Pagodas</h5>
                            <p class="text-gray">Ancient complex of over 2,000 stupas dating back to the 16th century. Pa-O cultural heritage site.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-shopping-basket text-danger fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Local Markets</h5>
                            <p class="text-gray">Rotating market system (5-day markets) where local Shan and Pa-O communities trade goods.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-home text-secondary fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Shan Villages</h5>
                            <p class="text-gray">Traditional stilt-house villages where you can experience local life and hospitality.</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 text-center">
                <span class="badge bg-purple-light text-purple p-2">
                    <i class="fas fa-camera me-1"></i> Must-See Places
                </span>
            </div>
        """,
        
        'activities': """
            <div class="activities-grid">
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-shuttle-van text-primary fa-2x mb-2"></i>
                            <h6 class="fw-bold">Airport Transfers</h6>
                            <small class="text-gray">Arranged transport from Heho to Inle Lake and surrounding areas</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-shopping-bag text-success fa-2x mb-2"></i>
                            <h6 class="fw-bold">Local Market Visits</h6>
                            <small class="text-gray">Experience authentic Shan markets on rotating market days</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-hiking text-warning fa-2x mb-2"></i>
                            <h6 class="fw-bold">Starting Point for Treks</h6>
                            <small class="text-gray">Base for trekking adventures to Kalaw and Shan villages</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-church text-info fa-2x mb-2"></i>
                            <h6 class="fw-bold">Cultural Stops</h6>
                            <small class="text-gray">Visit local monasteries and cultural sites en route to the lake</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-camera-retro text-danger fa-2x mb-2"></i>
                            <h6 class="fw-bold">Photography</h6>
                            <small class="text-gray">Capture stunning landscapes, local life, and rural scenes</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 text-center">
                <span class="badge bg-green-light text-green p-2">
                    <i class="fas fa-bicycle me-1"></i> Adventure & Experiences
                </span>
            </div>
        """,
        
        'cultural_info': """
            <div class="cultural-content">
                <p>Heho is situated in an area predominantly inhabited by the <strong>Shan</strong> ethnic group, with significant <strong>Pa-O</strong> communities in the surrounding hills. This cultural diversity creates a rich tapestry of traditions, festivals, and daily life.</p>
                
                <div class="cultural-highlight mt-4 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-leaf me-2 text-success"></i>Agricultural Heritage</h6>
                    <p class="mb-0 text-gray">The region is known for its agriculture, including rice paddies, vegetable farms, and increasingly, avocado and coffee plantations. Many local families still farm using traditional methods.</p>
                </div>
                
                <div class="cultural-highlight mt-3 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-church me-2 text-warning"></i>Religious Practices</h6>
                    <p class="mb-0 text-gray">Theravada Buddhism is central to local culture, with monasteries serving as community centers. You'll notice monks collecting alms in the early morning, a tradition that continues daily.</p>
                </div>
                
                <div class="cultural-highlight mt-3 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-tshirt me-2 text-info"></i>Traditional Dress</h6>
                    <p class="mb-0 text-gray">Shan women traditionally wear colorful blouses with longitudinal stripes and a longyi (sarong). Pa-O women are known for their distinctive black and indigo clothing with turbans.</p>
                </div>
            </div>
        """,
        
        'local_cuisine': """
            <div class="cuisine-content">
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-utensils text-danger me-2"></i>Shan Noodles</h6>
                    <p class="text-gray small mb-0">Rice noodles served with chicken or pork, in a light broth or dry with pickled vegetables and peanuts.</p>
                </div>
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-seedling text-success me-2"></i>Tea Leaf Salad</h6>
                    <p class="text-gray small mb-0">Fermented tea leaves mixed with nuts, peas, tomatoes, and garlic - a national favorite.</p>
                </div>
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-fish text-info me-2"></i>Local Vegetables</h6>
                    <p class="text-gray small mb-0">Fresh mountain vegetables often served in soups or stir-fries with local herbs.</p>
                </div>
            </div>
        """,
        
        'tips': """
            <div class="tips-list">
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Organize transport to Inle Lake in advance through your hotel</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Consider staying overnight if your flight requires it</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Visit local markets for authentic cultural experiences</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Try Shan food - it's distinct from other Myanmar cuisine</p>
            </div>
        """,
        
        'best_time_to_visit': 'October to March (Cool and dry season)',
    },
    
    # Add similar rich content for other destinations
    'Inle Lake': {
        'history': """
            <div class="history-content">
                <p>Inle Lake is a freshwater lake located in the Nyaungshwe Township of Taunggyi District, Shan State. It's the second largest lake in Myanmar with an estimated surface area of 44.9 square miles (116 km²).</p>
                
                <p>The lake's unique ecosystem and the lifestyle of its inhabitants have made it a major tourist destination. The Intha people, who live in stilt-house villages on the lake, are famous for their distinctive leg-rowing technique where they stand on one leg and wrap the other around the oar.</p>
                
                <div class="history-highlight mt-3 p-3 bg-light rounded">
                    <i class="fas fa-fish text-primary me-2"></i>
                    <strong>Did you know?</strong> The lake is home to several endemic species, including the Inle carp (called nga hpein in Burmese) and the Inle loach.
                </div>
            </div>
        """,
        
        'attractions': """
            <div class="attractions-grid">
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-water text-info fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Leg-Rowing Fishermen</h5>
                            <p class="text-gray">Witness the unique fishing technique where men row with one leg, leaving their hands free to handle the conical fishing net.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-home text-success fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Floating Villages</h5>
                            <p class="text-gray">Explore stilt-house communities like Ywama and Nam Pan, where houses, schools, and even gardens float on the lake.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-church text-warning fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Phaung Daw Oo Pagoda</h5>
                            <p class="text-gray">The most important religious site on the lake, housing five small Buddha images covered in gold leaf.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-pagoda text-danger fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Nga Phe Kyaung Monastery</h5>
                            <p class="text-gray">The oldest monastery on the lake, built in the 1850s, famous for its collection of Buddha images.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-shopping-bag text-secondary fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Floating Market</h5>
                            <p class="text-gray">The rotating market (every 5 days) where locals gather to trade goods from their boats.</p>
                        </div>
                    </div>
                </div>
                
                <div class="attraction-item mb-3">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-tshirt text-info fa-2x me-3 mt-1"></i>
                        <div>
                            <h5 class="fw-bold">Weaving Workshops</h5>
                            <p class="text-gray">Watch traditional silk and lotus weaving in villages like In Paw Khon.</p>
                        </div>
                    </div>
                </div>
            </div>
        """,
        
        'activities': """
            <div class="activities-grid">
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-ship text-primary fa-2x mb-2"></i>
                            <h6 class="fw-bold">Boat Tours</h6>
                            <small class="text-gray">Full-day boat trips exploring the lake's attractions</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-hiking text-success fa-2x mb-2"></i>
                            <h6 class="fw-bold">Trekking</h6>
                            <small class="text-gray">Multi-day treks to Kalaw through Shan villages</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-camera text-warning fa-2x mb-2"></i>
                            <h6 class="fw-bold">Sunset Photography</h6>
                            <small class="text-gray">Capture stunning sunset views over the lake</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-store text-info fa-2x mb-2"></i>
                            <h6 class="fw-bold">Market Days</h6>
                            <small class="text-gray">Visit the rotating 5-day markets</small>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="activity-card p-3 border rounded">
                            <i class="fas fa-fish text-danger fa-2x mb-2"></i>
                            <h6 class="fw-bold">Fishing Experience</h6>
                            <small class="text-gray">Learn traditional fishing techniques</small>
                        </div>
                    </div>
                </div>
            </div>
        """,
        
        'cultural_info': """
            <div class="cultural-content">
                <p>The lake is home to the <strong>Intha people</strong>, who have developed a unique culture adapted to life on the water. Surrounding hills are inhabited by <strong>Pa-O, Danu, and Shan</strong> ethnic groups.</p>
                
                <div class="cultural-highlight mt-4 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-water me-2 text-primary"></i>Floating Gardens</h6>
                    <p class="mb-0 text-gray">Local farmers create floating gardens from water hyacinth and mud, anchored to the lake bottom with bamboo poles. These gardens produce tomatoes, gourds, and flowers.</p>
                </div>
                
                <div class="cultural-highlight mt-3 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-tshirt me-2 text-success"></i>Traditional Crafts</h6>
                    <p class="mb-0 text-gray">The region is famous for lotus weaving, where threads are extracted from lotus stems and woven into cloth. You can watch this process in In Paw Khon village.</p>
                </div>
                
                <div class="cultural-highlight mt-3 p-3 bg-light rounded">
                    <h6 class="fw-bold"><i class="fas fa-calendar-alt me-2 text-warning"></i>Phaung Daw Oo Festival</h6>
                    <p class="mb-0 text-gray">Annual festival (October) where four of the five Buddha images from the pagoda are taken on a royal barge around the lake.</p>
                </div>
            </div>
        """,
        
        'local_cuisine': """
            <div class="cuisine-content">
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-fish text-info me-2"></i>Inle Carp</h6>
                    <p class="text-gray small mb-0">Freshwater fish unique to the lake, often grilled or in curries</p>
                </div>
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-seedling text-success me-2"></i>Shan Tofu</h6>
                    <p class="text-gray small mb-0">Made from chickpea flour, served in salads or soups</p>
                </div>
                <div class="cuisine-item mb-3">
                    <h6 class="fw-bold"><i class="fas fa-carrot text-warning me-2"></i>Floating Garden Tomatoes</h6>
                    <p class="text-gray small mb-0">Locally grown tomatoes from the famous floating gardens</p>
                </div>
            </div>
        """,
        
        'tips': """
            <div class="tips-list">
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Best time to visit is September-October during the Phaung Daw Oo Festival</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Book boat tours through your hotel</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Bring a jacket - mornings can be cool</p>
                <p class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Respect photography rules at religious sites</p>
            </div>
        """,
        
        'best_time_to_visit': 'September to March',
    },
    
    # Add Bagan, Mandalay, Yangon, etc. with similar rich content
}

def populate_rich_content():
    """Populate rich HTML content for destinations"""
    print("\n🚀 Starting rich content population...")
    
    for dest_name, content in RICH_CONTENT.items():
        try:
            destination = Destination.objects.get(name__iexact=dest_name)
            
            print(f"\n📝 Updating {dest_name}...")
            
            # Update text fields
            if 'history' in content:
                destination.history = content['history']
                print(f"  ✅ History updated")
                
            if 'attractions' in content:
                destination.attractions = content['attractions']
                print(f"  ✅ Attractions updated")
                
            if 'activities' in content:
                destination.activities = content['activities']
                print(f"  ✅ Activities updated")
                
            if 'cultural_info' in content:
                destination.cultural_info = content['cultural_info']
                print(f"  ✅ Cultural info updated")
                
            if 'local_cuisine' in content:
                destination.local_cuisine = content['local_cuisine']
                print(f"  ✅ Local cuisine updated")
                
            if 'tips' in content:
                destination.tips = content['tips']
                print(f"  ✅ Travel tips updated")
                
            if 'best_time_to_visit' in content:
                destination.best_time_to_visit = content['best_time_to_visit']
                print(f"  ✅ Best time updated")
            
            destination.save()
            print(f"  ✅ All changes saved for {dest_name}")
            
        except Destination.DoesNotExist:
            print(f"  ❌ Destination '{dest_name}' not found")
        except Exception as e:
            print(f"  ❌ Error updating {dest_name}: {str(e)}")
    
    print("\n🎉 Rich content population complete!")

if __name__ == "__main__":
    populate_rich_content()