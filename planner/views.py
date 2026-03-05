# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# COMPLETE CORRECTED VERSION
import json
from .models_room import Room, RoomType, RoomAvailability, RoomBooking
from django.db.models import Q, Count, Prefetch
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from .models_room import Room, RoomType, RoomBooking
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, datetime
import json
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import TripPlan
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from .models import TripPlan


import random
from django.conf import settings
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan, Airline, BookedSeat,TransportSchedule 
from .real_hotels_service import real_hotels_service
import urllib.parse  # Add this import for URL encoding
from .weather_service import WeatherService

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Add these imports at the top of the file
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import os
class DownloadItineraryPDFView(LoginRequiredMixin, View):
    """Generate and download itinerary as PDF using ReportLab"""
    def get(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            # Get itinerary data
            itinerary_generator = PlanSelectionView()
            days = trip.calculate_nights() + 1
            
            if plan_id == 'cultural':
                days_data = itinerary_generator.generate_cultural_itinerary(trip, days)
                plan_title = 'Cultural Explorer'
                plan_color = colors.HexColor('#3498db')  # Blue
            elif plan_id == 'adventure':
                days_data = itinerary_generator.generate_adventure_itinerary(trip, days)
                plan_title = 'Adventure Seeker'
                plan_color = colors.HexColor('#2ecc71')  # Green
            else:
                days_data = itinerary_generator.generate_relaxed_itinerary(trip, days)
                plan_title = 'Relaxed Wanderer'
                plan_color = colors.HexColor('#9b59b6')  # Purple
            
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create PDF document - Use A4 size
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=1*cm,
                bottomMargin=1*cm,
                leftMargin=1.5*cm,
                rightMargin=1.5*cm,
                title=f"{plan_title} Itinerary - {trip.destination.name}"
            )
            
            # Build story (content) for PDF
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=0.4*inch,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=plan_color,
                spaceAfter=0.3*inch,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            section_style = ParagraphStyle(
                'SectionStyle',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceBefore=0.2*inch,
                spaceAfter=0.1*inch,
                fontName='Helvetica-Bold',
                leftIndent=0,
                backColor=colors.HexColor('#f8f9fa'),
                borderPadding=5,
                borderColor=colors.HexColor('#3498db'),
                borderWidth=1
            )
            
            day_style = ParagraphStyle(
                'DayStyle',
                parent=styles['Heading4'],
                fontSize=12,
                textColor=colors.white,
                spaceBefore=0.3*inch,
                spaceAfter=0.1*inch,
                fontName='Helvetica-Bold',
                alignment=TA_LEFT,
                backColor=plan_color,
                borderPadding=8,
                borderRadius=4
            )
            
            activity_time_style = ParagraphStyle(
                'ActivityTime',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#3498db'),
                fontName='Helvetica-Bold',
                spaceAfter=2
            )
            
            activity_title_style = ParagraphStyle(
                'ActivityTitle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#2c3e50'),
                fontName='Helvetica-Bold',
                spaceAfter=3
            )
            
            activity_detail_style = ParagraphStyle(
                'ActivityDetail',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                spaceAfter=5,
                leftIndent=20
            )
            
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#999999'),
                alignment=TA_CENTER,
                spaceBefore=0.5*inch
            )
            
            # Label style for table headers
            label_style = ParagraphStyle(
                'LabelStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2c3e50'),
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT,
                rightIndent=5
            )
            
            value_style = ParagraphStyle(
                'ValueStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_LEFT,
                leftIndent=5
            )
            
            # ========== TITLE PAGE ==========
            # Main title
            story.append(Paragraph(f"{plan_title} Itinerary", title_style))
            story.append(Paragraph(f"{trip.destination.name}, Myanmar", subtitle_style))
            
            # Add a decorative line
            story.append(Spacer(1, 0.1*inch))
            story.append(Table(
                [[ "" ]],
                colWidths=[6*inch],
                style=TableStyle([
                    ('LINEABOVE', (0, 0), (0, 0), 2, plan_color),
                ])
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # ========== TRIP OVERVIEW ==========
            story.append(Paragraph("Trip Overview", section_style))
            
            # Trip summary table - FIXED: Use Paragraph objects instead of raw HTML
            summary_data = [
                [Paragraph("Destination:", label_style), 
                 Paragraph(f"{trip.destination.name}, {trip.destination.region}", value_style)],
                [Paragraph("Travel Dates:", label_style), 
                 Paragraph(f"{trip.start_date.strftime('%B %d, %Y')} to {trip.end_date.strftime('%B %d, %Y')}", value_style)],
                [Paragraph("Duration:", label_style), 
                 Paragraph(f"{days} days ({trip.calculate_nights()} nights)", value_style)],
                [Paragraph("Travelers:", label_style), 
                 Paragraph(f"{trip.travelers} person{'s' if trip.travelers > 1 else ''}", value_style)],
                [Paragraph("Travel Plan:", label_style), 
                 Paragraph(plan_title, value_style)],
                [Paragraph("Generated on:", label_style), 
                 Paragraph(timezone.now().strftime('%B %d, %Y at %I:%M %p'), value_style)],
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # ========== ACCOMMODATION DETAILS ==========
            if trip.selected_hotel:
                story.append(Paragraph("Accommodation Details", section_style))
                
                hotel = trip.selected_hotel
                hotel_data = [
                    [Paragraph("Hotel Name:", label_style), 
                     Paragraph(hotel.name, value_style)],
                    [Paragraph("Address:", label_style), 
                     Paragraph(hotel.address, value_style)],
                    [Paragraph("Category:", label_style), 
                     Paragraph(hotel.get_category_display(), value_style)],
                    [Paragraph("Price per Night:", label_style), 
                     Paragraph(hotel.price_in_mmk(), value_style)],
                ]
                
                if hotel.amenities:
                    amenities_text = ', '.join([a.replace('_', ' ').title() for a in hotel.get_amenities_list()[:5]])
                    if len(hotel.get_amenities_list()) > 5:
                        amenities_text += '...'
                    hotel_data.append([Paragraph("Amenities:", label_style), 
                                      Paragraph(amenities_text, value_style)])
                
                hotel_table = Table(hotel_data, colWidths=[1.5*inch, 4.5*inch])
                hotel_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (0, -1), 5),
                    ('LEFTPADDING', (1, 0), (1, -1), 5),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ]))
                story.append(hotel_table)
                story.append(Spacer(1, 0.3*inch))
            
            # ========== TRANSPORTATION DETAILS ==========
            if trip.selected_transport:
                story.append(Paragraph("Transportation Details", section_style))
                
                transport = trip.selected_transport
                transport_data = []
                
                if isinstance(transport, dict):
                    if transport.get('type') == 'flight':
                        transport_data = [
                            [Paragraph("Type:", label_style), Paragraph("Flight", value_style)],
                            [Paragraph("Airline:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('airline', 'N/A'), value_style)],
                            [Paragraph("Flight Number:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('flight_number', 'N/A'), value_style)],
                            [Paragraph("Departure:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('departure', 'N/A'), value_style)],
                            [Paragraph("Arrival:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('arrival', 'N/A'), value_style)],
                            [Paragraph("Travel Date:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('travel_date', 'N/A'), value_style)],
                            [Paragraph("Departure Time:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('departure_time', 'N/A'), value_style)],
                        ]
                    elif transport.get('type') == 'bus':
                        transport_data = [
                            [Paragraph("Type:", label_style), Paragraph("Bus", value_style)],
                            [Paragraph("Company:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('company', 'N/A'), value_style)],
                            [Paragraph("Bus Type:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('bus_type', 'N/A'), value_style)],
                            [Paragraph("Departure:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('departure', 'N/A'), value_style)],
                            [Paragraph("Arrival:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('arrival', 'N/A'), value_style)],
                            [Paragraph("Travel Date:", label_style), 
                             Paragraph(transport.get('booking_details', {}).get('travel_date', 'N/A'), value_style)],
                        ]
                    elif transport.get('type') == 'car':
                        company = transport.get('name', 'N/A').split(' - ')[0] if ' - ' in transport.get('name', '') else transport.get('name', 'N/A')
                        car_model = transport.get('name', 'N/A').split(' - ')[1] if ' - ' in transport.get('name', '') else 'N/A'
                        transport_data = [
                            [Paragraph("Type:", label_style), Paragraph("Car Rental", value_style)],
                            [Paragraph("Company:", label_style), Paragraph(company, value_style)],
                            [Paragraph("Car Model:", label_style), Paragraph(car_model, value_style)],
                            [Paragraph("Pickup Location:", label_style), 
                             Paragraph(trip.origin.name if trip.origin else 'N/A', value_style)],
                            [Paragraph("Travel Date:", label_style), 
                             Paragraph(trip.start_date.strftime('%B %d, %Y'), value_style)],
                        ]
                    else:
                        transport_data = [
                            [Paragraph("Type:", label_style), 
                             Paragraph(transport.get('type', 'N/A').title(), value_style)],
                            [Paragraph("Service:", label_style), 
                             Paragraph(transport.get('name', 'N/A'), value_style)],
                        ]
                else:
                    # If transport is not a dict, just show basic info
                    transport_data = [
                        [Paragraph("Transport:", label_style), 
                         Paragraph(str(transport)[:100], value_style)],
                    ]
                
                if transport_data:
                    transport_table = Table(transport_data, colWidths=[1.5*inch, 4.5*inch])
                    transport_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (0, -1), 5),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ]))
                    story.append(transport_table)
                
                story.append(Spacer(1, 0.3*inch))
            
            # Page break before daily itinerary
            story.append(PageBreak())
            
            # ========== DAILY ITINERARY ==========
            story.append(Paragraph("Daily Itinerary", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            for day_index, day in enumerate(days_data):
                # Check if day is a dictionary
                if isinstance(day, dict):
                    # Get day number and date from dictionary
                    day_number = day.get('day_number', day_index + 1)
                    day_date = day.get('date', '')
                    
                    # Day header
                    day_title = f"Day {day_number}: {day_date}"
                    story.append(Paragraph(day_title, day_style))
                    
                    # Get activities for the day
                    activities = day.get('activities', [])
                    
                    # Activities for the day
                    for activity_index, activity in enumerate(activities):
                        if isinstance(activity, dict):
                            # Activity time and title
                            time_text = activity.get('time', 'N/A')
                            story.append(Paragraph(time_text, activity_time_style))
                            
                            title_text = activity.get('title', 'Activity')
                            story.append(Paragraph(title_text, activity_title_style))
                            
                            # Activity details
                            details_text = ""
                            
                            location = activity.get('location')
                            if location:
                                details_text += f"<b>Location:</b> {location}<br/>"
                            
                            duration = activity.get('duration')
                            if duration:
                                details_text += f"<b>Duration:</b> {duration}<br/>"
                            
                            description = activity.get('description')
                            if description:
                                details_text += f"<b>Description:</b> {description}"
                            
                            if details_text:
                                story.append(Paragraph(details_text, activity_detail_style))
                            
                            # Add spacing between activities, but not after the last one
                            if activity_index < len(activities) - 1:
                                story.append(Spacer(1, 0.15*inch))
                                # Add a subtle separator
                                story.append(Table(
                                    [[ "" ]],
                                    colWidths=[6*inch],
                                    style=TableStyle([
                                        ('LINEABOVE', (0, 0), (0, 0), 0.5, colors.HexColor('#f0f0f0')),
                                    ])
                                ))
                                story.append(Spacer(1, 0.15*inch))
                
                # Add spacing between days, but not after the last day
                if day_index < len(days_data) - 1:
                    story.append(Spacer(1, 0.3*inch))
                    
                    # Check if we need a page break
                    if (day_index + 1) % 3 == 0:  # Every 3 days, add page break
                        story.append(PageBreak())
                        # Add header for new page
                        story.append(Paragraph("Daily Itinerary (continued)", section_style))
                        story.append(Spacer(1, 0.1*inch))
            
            # ========== IMPORTANT NOTES PAGE ==========
            story.append(PageBreak())
            story.append(Paragraph("Important Notes & Information", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Notes data - FIXED: Use proper Paragraph objects
            notes_categories = [
                ("Before You Travel", [
                    "Ensure your passport is valid for at least 6 months",
                    "Check visa requirements for Myanmar",
                    "Purchase travel insurance",
                    "Inform your bank about international travel",
                    "Download offline maps of your destination"
                ]),
                ("During Your Trip", [
                    "Keep photocopies of important documents separately",
                    "Respect local customs and dress modestly at religious sites",
                    "Carry local currency (MMK) for small purchases",
                    "Stay hydrated and use sunscreen",
                    "Be mindful of local laws and regulations"
                ]),
                ("Emergency Contacts", [
                    "Local Emergency: 199",
                    "Police: 199", 
                    "Fire: 191",
                    "Tourist Police: +95 1 549 622",
                    "Your Hotel: Contact information provided separately"
                ]),
                ("Health & Safety", [
                    "Drink bottled water only",
                    "Use mosquito repellent",
                    "Carry basic first aid supplies",
                    "Know the location of the nearest hospital",
                    "Have travel insurance contact details handy"
                ]),
            ]
            
            for category_title, items in notes_categories:
                story.append(Paragraph(category_title, section_style))
                
                # Create bullet points
                for item in items:
                    story.append(Paragraph(f"• {item}", ParagraphStyle(
                        'BulletStyle',
                        parent=styles['Normal'],
                        fontSize=9,
                        leftIndent=20,
                        spaceAfter=3
                    )))
                
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.3*inch))
            
            # ========== COST ESTIMATE ==========
            try:
                cost_breakdown = trip.get_cost_breakdown()
                if cost_breakdown and cost_breakdown.get('total', 0) > 0:
                    story.append(Paragraph("Cost Estimate", section_style))
                    
                    # Cost data - FIXED: Use proper formatting
                    cost_data = [
                        [Paragraph("Category", ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)),
                         Paragraph("Estimated Cost (MMK)", ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT))],
                        
                        [Paragraph("Hotel Accommodation", value_style),
                         Paragraph(f"{cost_breakdown.get('hotel', 0):,}", ParagraphStyle('ValueRight', parent=value_style, alignment=TA_RIGHT))],
                        
                        [Paragraph("Transportation", value_style),
                         Paragraph(f"{cost_breakdown.get('transport', 0):,}", ParagraphStyle('ValueRight', parent=value_style, alignment=TA_RIGHT))],
                        
                        [Paragraph("Activities & Meals", value_style),
                         Paragraph(f"{cost_breakdown.get('destination', 0):,}", ParagraphStyle('ValueRight', parent=value_style, alignment=TA_RIGHT))],
                    ]
                    
                    # Add additional travelers cost if applicable
                    additional_cost = cost_breakdown.get('additional_travelers', 0)
                    if additional_cost > 0:
                        cost_data.append([
                            Paragraph("Additional Travelers", value_style),
                            Paragraph(f"{additional_cost:,}", ParagraphStyle('ValueRight', parent=value_style, alignment=TA_RIGHT))
                        ])
                    
                    # Add total row
                    cost_data.append([
                        Paragraph("TOTAL ESTIMATED COST", ParagraphStyle('TotalLabel', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)),
                        Paragraph(f"{cost_breakdown.get('total', 0):,}", ParagraphStyle('TotalValue', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT))
                    ])
                    
                    cost_table = Table(cost_data, colWidths=[3.5*inch, 2.5*inch])
                    cost_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -3), 0.5, colors.HexColor('#e0e0e0')),
                        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#3498db')),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ]))
                    
                    story.append(cost_table)
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph('Note: Costs are estimates and may vary. All amounts in Myanmar Kyat (MMK).', 
                                          ParagraphStyle('NoteStyle', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))
            except Exception as cost_error:
                print(f"Cost calculation error: {cost_error}")
                # Continue without cost section if there's an error
            
            # ========== FOOTER ==========
            story.append(Spacer(1, 0.5*inch))
            footer_text = '''<b>Generated by GoMyanmar Travel Planner</b><br/>
            Thank you for choosing Myanmar for your adventure!<br/>
            For assistance or questions, contact: support@gomyanmar.com<br/>
            <font size="7">This itinerary is computer-generated. Please verify all details before travel.</font>'''
            
            story.append(Paragraph(footer_text, footer_style))
            
            # ========== BUILD PDF ==========
            doc.build(story)
            
            # Get PDF value from buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"{plan_title.lower().replace(' ', '_')}_{trip.destination.name.lower().replace(' ', '_')}_{timezone.now().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"PDF Generation Error: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('planner:itinerary_detail', trip_id=trip.id, plan_id=plan_id)


# planner/views_seats.py

import json
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    TripPlan,
    Flight,
    BusService,
    CarRental,
    TransportSchedule,
    BookedSeat
)


class SelectSeatsView(LoginRequiredMixin, View):

    template_name = "planner/select_seats.html"

    # =====================================================
    # GET → SHOW SEAT MAP
    # =====================================================
    def get(self, request, trip_id, transport_id):

        trip = get_object_or_404(
            TripPlan,
            id=trip_id,
            user=request.user
        )

        transport_type = request.GET.get("type", "flight")
        travel_date = trip.start_date

        # Get schedule
        schedule = get_object_or_404(
            TransportSchedule,
            transport_type=transport_type,
            transport_id=transport_id,
            travel_date=travel_date,
            is_active=True
        )

        # Check available seats
        if schedule.available_seats < trip.travelers:
            messages.error(
                request,
                f"Only {schedule.available_seats} seats left."
            )

            return redirect(
                "planner:select_transport",
                trip_id=trip.id
            )

        # Route by transport type
        if transport_type == "flight":
            return self.flight_seats(request, trip, transport_id, schedule)

        elif transport_type == "bus":
            return self.bus_seats(request, trip, transport_id, schedule)

        elif transport_type == "car":
            return self.car_rental(request, trip, transport_id, schedule)

        messages.error(request, "Invalid transport type")

        return redirect(
            "planner:select_transport",
            trip_id=trip.id
        )

    # =====================================================
    # POST → SAVE SELECTED SEATS
    # =====================================================
    def post(self, request, trip_id, transport_id):

        trip = get_object_or_404(
            TripPlan,
            id=trip_id,
            user=request.user
        )

        transport_type = request.POST.get("transport_type")
        travel_date = trip.start_date

        # Get selected seats
        try:
            selected_seats = json.loads(
                request.POST.get("selected_seats", "[]")
            )
        except:
            selected_seats = []

        if not selected_seats and transport_type != "car":
            messages.error(request, "Please select seats first.")

            return redirect(
                "planner:select_seats",
                trip_id=trip.id,
                transport_id=transport_id
            )

        # Get schedule
        schedule = get_object_or_404(
            TransportSchedule,
            transport_type=transport_type,
            transport_id=transport_id,
            travel_date=travel_date,
            is_active=True
        )

        # Already booked seats
        booked_seats = list(
            BookedSeat.objects.filter(
                transport_type=transport_type,
                transport_id=transport_id,
                schedule_date=travel_date,
                is_cancelled=False
            ).values_list("seat_number", flat=True)
        )

        # Validate seats
        for seat in selected_seats:
            if seat in booked_seats:
                messages.error(
                    request,
                    f"Seat {seat} is already booked."
                )

                return redirect(
                    "planner:select_seats",
                    trip_id=trip.id,
                    transport_id=transport_id
                )

        # Booking reference
        booking_ref = f"TEMP{random.randint(10000, 99999)}"

        total_price = float(
            request.POST.get("total_price", 0)
        )

        # Save in trip JSON field
        trip.selected_transport = {

            "type": transport_type,
            "id": transport_id,
            "schedule_id": schedule.id,
            "seats": selected_seats,

            "booking_details": {
                "total_price": total_price,
                "price_per_seat": (
                    total_price / len(selected_seats)
                    if selected_seats else 0
                ),
            },

            "booking_id": booking_ref,
            "is_temporary": True,
            "needs_confirmation": True,
        }

        trip.status = "planning"
        trip.save()

        messages.success(
            request,
            "Seats saved (Pending confirmation)"
        )

        return redirect(
            "planner:plan_selection",
            trip_id=trip.id
        )

    # =====================================================
    # FLIGHT VIEW
    # =====================================================
    def flight_seats(self, request, trip, transport_id, schedule):

        transport = get_object_or_404(
            Flight,
            id=transport_id
        )

        occupied = self.get_occupied(
            "flight",
            transport_id,
            trip.start_date
        )

        seat_layout = self.build_flight_layout(occupied)

        context = {
            "trip": trip,
            "transport": transport,
            "schedule": schedule,
            "occupied": occupied,
            "seat_layout": seat_layout,
            "transport_type": "flight",
            "travel_date": trip.start_date,
            "available_seats": schedule.available_seats,
        }

        return render(
            request,
            self.template_name,
            context
        )

    # =====================================================
    # BUS VIEW
    # =====================================================
    def bus_seats(self, request, trip, transport_id, schedule):

        transport = get_object_or_404(
            BusService,
            id=transport_id
        )

        occupied = self.get_occupied(
            "bus",
            transport_id,
            trip.start_date
        )

        seat_layout = self.build_bus_layout(occupied)

        context = {
            "trip": trip,
            "transport": transport,
            "schedule": schedule,
            "occupied": occupied,
            "seat_layout": seat_layout,
            "transport_type": "bus",
            "travel_date": trip.start_date,
            "available_seats": schedule.available_seats,
        }

        return render(
            request,
            self.template_name,
            context
        )

    # =====================================================
    # CAR RENTAL
    # =====================================================
    def car_rental(self, request, trip, transport_id, schedule):

        transport = get_object_or_404(
            CarRental,
            id=transport_id
        )

        trip.selected_transport = {

            "type": "car",
            "id": transport_id,
            "schedule_id": schedule.id,

            "is_temporary": False,
            "needs_confirmation": False,
        }

        trip.status = "planning"
        trip.save()

        messages.success(
            request,
            "Car selected successfully."
        )

        return redirect(
            "planner:plan_selection",
            trip_id=trip.id
        )

    # =====================================================
    # GET OCCUPIED SEATS
    # =====================================================
    def get_occupied(self, t_type, t_id, date):

        return list(
            BookedSeat.objects.filter(
                transport_type=t_type,
                transport_id=t_id,
                schedule_date=date,
                is_cancelled=False
            ).values_list("seat_number", flat=True)
        )

    # =====================================================
    # BUILD BUS LAYOUT
    # =====================================================
    def build_bus_layout(self, occupied):

        layout = []

        rows = 10   # 10 rows
        cols = ["A", "B", "C", "D"]

        for r in range(1, rows + 1):

            row = {
                "row_number": r,
                "seats": []
            }

            for c in cols:

                seat_no = f"{r}{c}"

                row["seats"].append({

                    "number": seat_no,
                    "occupied": seat_no in occupied,
                    "type": "normal",
                    "price_multiplier": 1,
                    "is_window": c in ["A", "D"]

                })

            layout.append(row)

        return layout

    # =====================================================
    # BUILD FLIGHT LAYOUT
    # =====================================================
    def build_flight_layout(self, occupied):

        layout = []

        rows = 20
        cols = ["A", "B", "C", "D", "E", "F"]

        for r in range(1, rows + 1):

            row_data = {
                "row_number": r,
                "is_first_class": r <= 2,
                "is_business_class": False,
                "seats": []
            }

            for c in cols:

                seat_no = f"{r}{c}"

                # Seat type
                if r <= 2:
                    seat_type = "first"
                    multiplier = 2.0
                elif r <= 5:
                    seat_type = "premium"
                    multiplier = 1.5
                else:
                    seat_type = "economy"
                    multiplier = 1

                row_data["seats"].append({

                    "number": seat_no,
                    "occupied": seat_no in occupied,
                    "type": seat_type,
                    "price_multiplier": multiplier,
                    "is_window": c in ["A", "F"]

                })

            layout.append(row_data)

        return layout

# IN THE DashboardView CLASS, UPDATE THE get_context_data METHOD:
# ========== CONFIRM SEAT BOOKING VIEW ==========
class ConfirmSeatBookingView(LoginRequiredMixin, View):

    def post(self, request, trip_id):

        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)

        data = trip.selected_transport

        if not data or not data.get("is_temporary"):
            messages.error(request, "Nothing to confirm")
            return redirect('planner:plan_selection', trip_id=trip.id)

        success = self.book_seats(trip, request)

        if not success:
            messages.error(request, "Seat booking failed")
            return redirect('planner:plan_selection', trip_id=trip.id)

        messages.success(request, "Seats confirmed")

        return redirect('planner:itinerary_detail',
                        trip_id=trip.id,
                        plan_id="cultural")


    def book_seats(self, trip, request):

        try:

            data = trip.selected_transport

            t_type = data["type"]
            t_id = data["id"]
            seats = data["seats"]
            date = trip.start_date

            schedule = get_object_or_404(
                TransportSchedule,
                transport_type=t_type,
                transport_id=t_id,
                travel_date=date,
                is_active=True
            )

            for seat in seats:

                BookedSeat.objects.create(
                    transport_type=t_type,
                    transport_id=t_id,
                    schedule_date=date,
                    seat_number=seat,
                    trip=trip,
                    booked_by=request.user
                )

            schedule.available_seats -= len(seats)
            schedule.save()

            trip.selected_transport["is_temporary"] = False
            trip.selected_transport["needs_confirmation"] = False

            trip.status = "booked"
            trip.save()

            return True

        except Exception as e:
            print("CONFIRM ERROR:", e)
            return False

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()  # Dynamic date
        
        # Get all trips for this user
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Calculate statistics
        total_trips = trips.count()
        
        # Upcoming trips (status: draft, planning, booked AND start_date in future)
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=today
        ).count()
        
        # Total spent (only for booked and completed trips)
        total_spent = 0
        for trip in trips.filter(status__in=['booked', 'completed']):
            total_spent += trip.get_total_cost_in_mmk()
        
        # Unique destinations visited (trips that have ended)
        destinations_visited = trips.filter(
            Q(status='completed') | Q(end_date__lt=today)
        ).exclude(
            status='cancelled'
        ).values('destination__name').distinct().count()
        
        print(f"DASHBOARD DEBUG: Today: {today}, Destinations visited: {destinations_visited}")
        
        # Get upcoming trips for display
        upcoming_trips_list = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=today
        ).order_by('start_date')[:3]
        
        # Prepare upcoming trips data for template
        upcoming_trips_data = []
        for trip in upcoming_trips_list:
            upcoming_trips_data.append({
                'id': trip.id,
                'title': f"{trip.destination.name} Trip",
                'date_range': f"{trip.start_date.strftime('%b %d')} - {trip.end_date.strftime('%b %d, %Y')}",
                'travelers': trip.travelers,
                'status': trip.status,
                'cost': trip.get_total_cost_in_mmk(),
                'destination_name': trip.destination.name
            })
        
        context.update({
            'trips': trips,
            'total_trips': total_trips,
            'upcoming_trips': upcoming_trips,
            'total_spent': total_spent,
            'destinations_visited': destinations_visited,
            'upcoming_trips_list': upcoming_trips_data,
            'today': today,
        })
        
        return context


# ========== PLAN TRIP VIEW ==========
class PlanTripView(LoginRequiredMixin, View):
    template_name = 'planner/plan.html'
    
    def get(self, request):
        # Check if we're coming from clear action
        clear_action = request.GET.get('clear', False)
        if clear_action:
            # Clear session data
            session_keys = list(request.session.keys())
            for key in session_keys:
                if any(term in key for term in ['hotel', 'transport', 'selected', 'trip']):
                    del request.session[key]
            request.session.modified = True
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # ALWAYS GET URL PARAMETERS FIRST
        origin_id = request.GET.get('origin_id')
        origin_name = request.GET.get('origin_name')
        destination_id = request.GET.get('destination_id')
        destination_name = request.GET.get('destination_name')
        start_date_param = request.GET.get('start_date')
        end_date_param = request.GET.get('end_date')
        travelers_param = request.GET.get('travelers')
        hotel_id = request.GET.get('hotel_id')
        hotel_name = request.GET.get('hotel_name')
        transport_id = request.GET.get('transport_id')
        transport_type = request.GET.get('transport_type')
        transport_name = request.GET.get('transport_name')
        
        # Initialize context with empty/default values
        context = {
            'today': today.strftime('%Y-%m-%d'),
            'tomorrow': tomorrow.strftime('%Y-%m-%d'),
            'origin_input': '',
            'selected_origin_id': '',
            'destination_input': '',
            'selected_destination_id': '',
            'selected_hotel_id': '',
            'selected_hotel_name': '',
            'selected_transport_id': '',
            'selected_transport_type': '',
            'selected_transport_name': '',
            'travelers': 2,
            'trip': None,  # Initialize trip as None
        }
        
        # If clear action was performed, don't restore any previous data
        if clear_action:
            return render(request, self.template_name, context)
        
        # 1. FIRST PRIORITY: URL parameters
        if origin_id and origin_name:
            context['selected_origin_id'] = origin_id
            context['origin_input'] = origin_name
        if destination_id and destination_name:
            context['selected_destination_id'] = destination_id
            context['destination_input'] = destination_name
        if start_date_param:
            context['today'] = start_date_param
        if end_date_param:
            context['tomorrow'] = end_date_param
        if travelers_param:
            context['travelers'] = int(travelers_param)
        if hotel_id and hotel_name:
            context['selected_hotel_id'] = hotel_id
            context['selected_hotel_name'] = hotel_name
        if transport_id and transport_name:
            context['selected_transport_id'] = transport_id
            context['selected_transport_type'] = transport_type
            context['selected_transport_name'] = transport_name
        
        # 2. SECOND PRIORITY: Session data
        if not context['selected_hotel_id']:
            context['selected_hotel_id'] = request.session.get('selected_hotel_id', '')
            context['selected_hotel_name'] = request.session.get('selected_hotel_name', '')
        
        if not context['selected_transport_id']:
            context['selected_transport_id'] = request.session.get('selected_transport_id', '')
            context['selected_transport_type'] = request.session.get('selected_transport_type', '')
            context['selected_transport_name'] = request.session.get('selected_transport_name', '')
        
        # 3. THIRD PRIORITY: Existing trip in database
        if not (origin_id and destination_id):
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                # Add trip to context
                context['trip'] = existing_trip
                
                # Restore data from existing trip
                if not context['origin_input'] and existing_trip.origin:
                    context['origin_input'] = existing_trip.origin.name
                    context['selected_origin_id'] = existing_trip.origin.id
                if not context['destination_input'] and existing_trip.destination:
                    context['destination_input'] = existing_trip.destination.name
                    context['selected_destination_id'] = existing_trip.destination.id
                if not context['selected_hotel_id'] and existing_trip.selected_hotel:
                    context['selected_hotel_id'] = existing_trip.selected_hotel.id
                    context['selected_hotel_name'] = existing_trip.selected_hotel.name
                if not context['selected_transport_id'] and existing_trip.selected_transport:
                    context['selected_transport_id'] = existing_trip.selected_transport.get('id', '')
                    context['selected_transport_type'] = existing_trip.selected_transport.get('type', '')
                    context['selected_transport_name'] = existing_trip.selected_transport.get('name', '')
                if not start_date_param and existing_trip.start_date:
                    context['today'] = existing_trip.start_date.strftime('%Y-%m-%d')
                if not end_date_param and existing_trip.end_date:
                    context['tomorrow'] = existing_trip.end_date.strftime('%Y-%m-%d')
                if not travelers_param and existing_trip.travelers:
                    context['travelers'] = existing_trip.travelers
        
        # 4. FOURTH PRIORITY: Individual GET parameters
        if not hotel_id and request.GET.get('hotel_id'):
            try:
                hotel = Hotel.objects.get(id=request.GET.get('hotel_id'))
                context['selected_hotel_id'] = hotel.id
                context['selected_hotel_name'] = hotel.name
            except Hotel.DoesNotExist:
                pass
        
        if not transport_id and request.GET.get('transport_id'):
            context['selected_transport_id'] = request.GET.get('transport_id')
            context['selected_transport_type'] = request.GET.get('transport_type', '')
            context['selected_transport_name'] = request.GET.get('transport_name', '')
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle both regular form submission and AJAX requests"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request)
        else:
            # Handle regular form submission
            return self.handle_form_submission(request)
    
    def handle_ajax(self, request):
        """Handle AJAX requests for saving trip info"""
        try:
            origin_id = request.POST.get('origin_id')
            destination_id = request.POST.get('destination_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            travelers = request.POST.get('travelers', 1)
            hotel_id = request.POST.get('hotel_id')
            transport_id = request.POST.get('transport_id')
            transport_type = request.POST.get('transport_type')
            
            if not all([origin_id, destination_id, start_date, end_date]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            if origin_id == destination_id:
                return JsonResponse({'success': False, 'error': 'Origin and destination cannot be the same'})
            
            # Parse dates
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date format'})
            
            if end_date_obj <= start_date_obj:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
            
            # Save hotel and transport to session
            if hotel_id:
                try:
                    hotel = Hotel.objects.get(id=hotel_id)
                    request.session['selected_hotel_id'] = hotel_id
                    request.session['selected_hotel_name'] = hotel.name
                except Hotel.DoesNotExist:
                    pass
            
            if transport_id and transport_type:
                request.session['selected_transport_id'] = transport_id
                request.session['selected_transport_type'] = transport_type
                
                # Get transport name
                transport_name = ''
                if transport_type == 'flight':
                    try:
                        transport = Flight.objects.get(id=transport_id)
                        transport_name = f"{transport.airline} Flight {transport.flight_number}"
                    except Flight.DoesNotExist:
                        pass
                elif transport_type == 'bus':
                    try:
                        transport = BusService.objects.get(id=transport_id)
                        transport_name = f"{transport.company} Bus"
                    except BusService.DoesNotExist:
                        pass
                elif transport_type == 'car':
                    try:
                        transport = CarRental.objects.get(id=transport_id)
                        transport_name = f"{transport.company} - {transport.car_model}"
                    except CarRental.DoesNotExist:
                        pass
                
                request.session['selected_transport_name'] = transport_name
            
            # Get or create trip
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                trip = existing_trip
                trip.origin_id = origin_id
                trip.destination_id = destination_id
                trip.start_date = start_date_obj
                trip.end_date = end_date_obj
                trip.travelers = travelers
                if hotel_id:
                    trip.selected_hotel_id = hotel_id
                if transport_type:
                    trip.transportation_preference = transport_type
                trip.status = 'planning'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    origin_id=origin_id,
                    destination_id=destination_id,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    travelers=travelers,
                    selected_hotel_id=hotel_id if hotel_id else None,
                    transportation_preference=transport_type if transport_type else '',
                    budget_range='medium',
                    status='planning'
                )
            
            # Save transport details to trip if transport is selected
            if transport_id and transport_type:
                if transport_type == 'flight':
                    try:
                        transport = Flight.objects.get(id=transport_id)
                        transport_name = f"{transport.airline} Flight {transport.flight_number}"
                        # FIX: Convert Decimal to float for JSON serialization
                        price = float(getattr(transport, 'price', 0))
                        trip.selected_transport = {
                            'type': transport_type,
                            'id': transport_id,
                            'name': transport_name,
                            'price': price  # Now it's a float
                        }
                    except Flight.DoesNotExist:
                        pass
                elif transport_type == 'bus':
                    try:
                        transport = BusService.objects.get(id=transport_id)
                        transport_name = f"{transport.company} Bus"
                        # FIX: Convert Decimal to float for JSON serialization
                        price = float(getattr(transport, 'price', 0))
                        trip.selected_transport = {
                            'type': transport_type,
                            'id': transport_id,
                            'name': transport_name,
                            'price': price  # Now it's a float
                        }
                    except BusService.DoesNotExist:
                        pass
                elif transport_type == 'car':
                    try:
                        transport = CarRental.objects.get(id=transport_id)
                        transport_name = f"{transport.company} - {transport.car_model}"
                        # FIX: Convert Decimal to float for JSON serialization
                        price = float(getattr(transport, 'price_per_day', 0))
                        trip.selected_transport = {
                            'type': transport_type,
                            'id': transport_id,
                            'name': transport_name,
                            'price': price  # Now it's a float
                        }
                    except CarRental.DoesNotExist:
                        pass
            
            trip.save()
            
            return JsonResponse({
                'success': True,
                'trip_id': trip.id,
                'message': 'Trip saved successfully'
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"AJAX Error: {error_details}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    def handle_form_submission(self, request):
        """Handle regular form submission (when Continue button is clicked)"""
        try:
            origin_id = request.POST.get('origin_id')
            destination_id = request.POST.get('destination_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            travelers = request.POST.get('travelers', 1)
            hotel_id = request.POST.get('selected_hotel_id')
            transport_id = request.POST.get('selected_transport_id')
            transport_type = request.POST.get('selected_transport_type')
            
            # Validate required fields
            if not all([origin_id, destination_id, start_date, end_date, hotel_id, transport_id]):
                messages.error(request, 'Please fill in all required fields and select both hotel and transport.')
                return redirect('planner:plan')
            
            # Parse dates
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('planner:plan')
            
            if end_date_obj <= start_date_obj:
                messages.error(request, 'End date must be after start date.')
                return redirect('planner:plan')
            
            # Clear session selections (start fresh)
            request.session.pop('selected_hotel_id', None)
            request.session.pop('selected_hotel_name', None)
            request.session.pop('selected_transport_id', None)
            request.session.pop('selected_transport_type', None)
            request.session.pop('selected_transport_name', None)
            
            # Get or create trip
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                trip = existing_trip
                trip.origin_id = origin_id
                trip.destination_id = destination_id
                trip.start_date = start_date_obj
                trip.end_date = end_date_obj
                trip.travelers = travelers
                trip.selected_hotel_id = hotel_id
                trip.transportation_preference = transport_type
                trip.status = 'planning'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    origin_id=origin_id,
                    destination_id=destination_id,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    travelers=travelers,
                    selected_hotel_id=hotel_id,
                    transportation_preference=transport_type,
                    budget_range='medium',
                    status='planning'
                )
            
            # Save transport details - FIXED: Convert Decimal to float
            if transport_id:
                if transport_type == 'flight':
                    transport = Flight.objects.get(id=transport_id)
                    transport_name = f"{transport.airline} Flight {transport.flight_number}"
                    transport_price = float(getattr(transport, 'price', 0))
                elif transport_type == 'bus':
                    transport = BusService.objects.get(id=transport_id)
                    transport_name = f"{transport.company} Bus"
                    transport_price = float(getattr(transport, 'price', 0))
                elif transport_type == 'car':
                    transport = CarRental.objects.get(id=transport_id)
                    transport_name = f"{transport.company} - {transport.car_model}"
                    transport_price = float(getattr(transport, 'price_per_day', 0))
                else:
                    messages.error(request, 'Invalid transport type.')
                    return redirect('planner:plan')
                
                trip.selected_transport = {
                    'type': transport_type,
                    'id': transport_id,
                    'name': transport_name,
                    'price': transport_price  # Now it's a float
                }
            
            trip.save()
            
            # Clear any existing plan selection for this specific trip
            request.session.pop(f'selected_plan_{trip.id}', None)
            request.session.modified = True
            
            # For AJAX requests, return success with trip_id
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'trip_id': trip.id,
                    'message': 'Trip saved successfully'
                })
            else:
                # For regular form submission, redirect to plan selection
                return redirect('planner:plan_selection', trip_id=trip.id)
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            else:
                messages.error(request, f'Error saving trip: {str(e)}')
                return redirect('planner:plan')        
# ========== DESTINATION SEARCH (AUTO-COMPLETE) ==========
# ========== DESTINATION SEARCH (AUTO-COMPLETE) - FIXED ==========
class DestinationSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        try:
            # IMPORTANT: Filter to ONLY cities and towns (NO attractions, NO regions)
            if len(query) == 1:
                destinations = Destination.objects.filter(
                    Q(name__istartswith=query) | Q(region__istartswith=query),
                    type__in=['city', 'town'],  # ← ONLY cities and towns
                    is_active=True
                ).order_by('name')[:20]
            else:
                destinations = Destination.objects.filter(
                    Q(name__icontains=query) | 
                    Q(region__icontains=query),
                    type__in=['city', 'town'],  # ← ONLY cities and towns
                    is_active=True
                ).order_by('name')[:15]
            
            results = []
            for dest in destinations:
                results.append({
                    'id': dest.id,
                    'name': dest.name,
                    'region': dest.region,
                    'type': dest.get_type_display(),
                    'full_name': f"{dest.name}, {dest.region}",
                    'has_coordinates': bool(dest.latitude and dest.longitude)
                })
            
            # If no results, show popular cities as fallback
            if not results and len(query) >= 1:
                popular_cities = ['Yangon', 'Mandalay', 'Bagan', 'Taunggyi', 'Naypyidaw', 
                                 'Mawlamyine', 'Pathein', 'Pyin Oo Lwin']
                destinations = Destination.objects.filter(
                    name__in=popular_cities,
                    type__in=['city', 'town'],  # ← ONLY cities and towns
                    is_active=True
                ).order_by('name')[:5]
                
                for dest in destinations:
                    results.append({
                        'id': dest.id,
                        'name': dest.name,
                        'region': dest.region,
                        'type': dest.get_type_display(),
                        'full_name': f"{dest.name}, {dest.region}",
                        'has_coordinates': bool(dest.latitude and dest.longitude)
                    })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f"Error searching destinations: {e}")
            return JsonResponse({'results': [], 'error': str(e)})

# ========== HOTEL SELECTION WITH MAP ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Replace the entire SelectHotelWithMapView class with this:
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Replace the SelectHotelWithMapView class with this SIMPLER version:
# ========== HOTEL SELECTION WITH MAP ==========

# ========== HOTEL SELECTION WITH MAP ==========
# ========== HOTEL SELECTION WITH MAP ==========


# ========== SELECT HOTEL WITH MAP VIEW ==========
# ========== SELECT HOTEL WITH MAP VIEW ==========
# In the same views.py file, update SelectHotelWithMapView
class SelectHotelWithMapView(LoginRequiredMixin, View):
    """View for selecting hotels with SIMPLE Google Maps iframe embeds (NO API KEY)"""
    template_name = 'planner/select_hotel_map_simple.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        nights = trip.calculate_nights()
        
        # Get filter parameters from request
        category_filter = request.GET.get('category', 'all')
        amenities_filter = request.GET.getlist('amenities')
        search_query = request.GET.get('search', '').strip()
        
        print(f"🔍 DEBUG: Starting hotel filtering")
        print(f"🔍 DEBUG: Destination: {trip.destination.name}")
        print(f"🔍 DEBUG: Category filter: {category_filter}")
        print(f"🔍 DEBUG: Amenities filter: {amenities_filter}")
        print(f"🔍 DEBUG: Search query: '{search_query}'")
        
        # Get hotels for this destination from YOUR DATABASE
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        )
        
        print(f"🔍 DEBUG: Initial hotels found: {hotels.count()}")
        
        # Apply search filter
        if search_query:
            print(f"🔍 DEBUG: Applying search filter: '{search_query}'")
            hotels = hotels.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query)
            )
            print(f"🔍 DEBUG: After search filter: {hotels.count()}")
        
        # Apply category filter
        if category_filter != 'all':
            print(f"🔍 DEBUG: Applying category filter: {category_filter}")
            if category_filter == 'budget':
                hotels = hotels.filter(category='budget')
            elif category_filter == 'medium':
                hotels = hotels.filter(category='medium')
            elif category_filter == 'luxury' or category_filter == 'high':
                hotels = hotels.filter(category__in=['luxury', 'high'])
            print(f"🔍 DEBUG: After category filter: {hotels.count()}")
        
        # Apply amenities filter - NEW: Use the same logic as FilterHotelsView
        if amenities_filter:
            print(f"🔍 DEBUG: Applying amenities filter: {amenities_filter}")
            
            # Clean and normalize amenities
            clean_amenities = []
            for amenity in amenities_filter:
                if amenity and amenity.strip():
                    clean_amenity = amenity.strip().lower().replace(' ', '_')
                    clean_amenities.append(clean_amenity)
            
            print(f"🔍 DEBUG: Cleaned amenities: {clean_amenities}")
            
            if clean_amenities:
                # Manually filter for ALL amenities
                filtered_hotels = []
                
                for hotel in hotels:
                    hotel_has_all_amenities = True
                    
                    if hotel.amenities and isinstance(hotel.amenities, list):
                        hotel_amenities_lower = []
                        for hotel_amenity in hotel.amenities:
                            if isinstance(hotel_amenity, str):
                                normalized_hotel_amenity = hotel_amenity.strip().lower().replace(' ', '_')
                                hotel_amenities_lower.append(normalized_hotel_amenity)
                        
                        for selected_amenity in clean_amenities:
                            if selected_amenity not in hotel_amenities_lower:
                                hotel_has_all_amenities = False
                                break
                        
                        if hotel_has_all_amenities:
                            filtered_hotels.append(hotel)
                
                # Create a new queryset from filtered hotels
                hotel_ids = [h.id for h in filtered_hotels]
                hotels = hotels.filter(id__in=hotel_ids)
                
                print(f"🔍 DEBUG: After amenities filter: {hotels.count()} hotels")
        
        # Default order by price
        hotels = hotels.order_by('price_per_night')
        
        print(f"🔍 DEBUG: Final hotel count: {hotels.count()}")
        
        # Get all unique amenities for this destination - FIXED
        all_amenities = set()
        for hotel in Hotel.objects.filter(destination=trip.destination, is_active=True):
            if hotel.amenities:
                if isinstance(hotel.amenities, list):
                    for amenity in hotel.amenities:
                        if amenity and isinstance(amenity, str):
                            # Normalize for display (replace underscores with spaces, title case)
                            display_amenity = amenity.replace('_', ' ').title()
                            all_amenities.add(display_amenity)
        
        print(f"🔍 DEBUG: Total unique amenities found: {len(all_amenities)}")
        
        # Prepare hotel data with Google Maps embed URL
        hotel_data = []
        for hotel in hotels:
            # Get image URL safely
            image_url = ''
            if hotel.image and hasattr(hotel.image, 'url'):
                try:
                    image_url = hotel.image.url
                except:
                    image_url = ''
            
            # Create Google Maps search query for iframe
            maps_query = f"{hotel.name} {hotel.address} {trip.destination.name} Myanmar"
            maps_query_encoded = urllib.parse.quote(maps_query)
            
            # Generate iframe URL (NO API KEY NEEDED)
            iframe_url = f"https://maps.google.com/maps?width=100%&height=300&hl=en&q={maps_query_encoded}&t=&z=14&ie=UTF8&iwloc=B&output=embed"
            
            # Get amenities as list for display
            hotel_amenities_display = []
            if hotel.amenities:
                if isinstance(hotel.amenities, list):
                    hotel_amenities_display = [str(a).replace('_', ' ').title() for a in hotel.amenities if a]
                elif isinstance(hotel.amenities, str):
                    try:
                        parsed = json.loads(hotel.amenities)
                        if isinstance(parsed, list):
                            hotel_amenities_display = [str(a).replace('_', ' ').title() for a in parsed if a]
                        else:
                            hotel_amenities_display = [hotel.amenities.replace('_', ' ').title()]
                    except:
                        hotel_amenities_display = [hotel.amenities.replace('_', ' ').title()]
            
            hotel_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'address': hotel.address,
                'price': float(hotel.price_per_night),
                'price_display': hotel.price_in_mmk(),
                'rating': float(hotel.rating),
                'review_count': hotel.review_count,
                'category': hotel.category,
                'category_display': hotel.get_category_display(),
                'amenities': hotel_amenities_display[:8],
                'amenities_count': len(hotel_amenities_display),
                'description': hotel.description[:100] + '...' if hotel.description and len(hotel.description) > 100 else (hotel.description or ''),
                'image_url': image_url,
                'phone_number': hotel.phone_number or '',
                'website': hotel.website or '',
                'has_image': bool(image_url),
                'maps_query': maps_query,
                'iframe_url': iframe_url,
                'has_coordinates': bool(hotel.latitude and hotel.longitude),
            })
        
        print(f"🔍 DEBUG: Prepared {len(hotel_data)} hotels for display")
        
        # Sort amenities alphabetically for display
        sorted_amenities = sorted(list(all_amenities))
        
        context = {
            'trip': trip,
            'hotels': hotel_data,
            'nights': nights,
            'destination_name': trip.destination.name,
            'destination_id': trip.destination.id,
            'today': timezone.now().date(),
            'all_amenities': sorted_amenities,
            'selected_category': category_filter,
            'selected_amenities': amenities_filter,
            'search_query': search_query,
        }
        return render(request, self.template_name, context)
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
class FilterHotelsView(View):
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        # Get all filter parameters
        category = request.GET.get('category', 'all')
        amenities = request.GET.getlist('amenities[]', [])
        search_query = request.GET.get('search', '').strip()
        
        print(f"🔍 DEBUG [FilterHotelsView]: Starting hotel filtering")
        print(f"🔍 DEBUG [FilterHotelsView]: Destination: {destination.name}")
        print(f"🔍 DEBUG [FilterHotelsView]: Category: {category}")
        print(f"🔍 DEBUG [FilterHotelsView]: Amenities: {amenities}")
        print(f"🔍 DEBUG [FilterHotelsView]: Search query: '{search_query}'")
        
        # Start with all hotels for this destination
        hotels = Hotel.objects.filter(
            destination=destination,
            is_active=True
        )
        
        print(f"🔍 DEBUG [FilterHotelsView]: Initial hotels: {hotels.count()}")
        
        # Apply search filter
        if search_query:
            print(f"🔍 DEBUG [FilterHotelsView]: Applying search: '{search_query}'")
            hotels = hotels.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query)
            )
            print(f"🔍 DEBUG [FilterHotelsView]: After search: {hotels.count()}")
        
        # Apply category filter
        if category != 'all':
            if category == 'budget':
                hotels = hotels.filter(category='budget')
            elif category == 'medium':
                hotels = hotels.filter(category='medium')
            elif category == 'luxury':
                hotels = hotels.filter(category__in=['luxury', 'high'])
            print(f"🔍 DEBUG [FilterHotelsView]: After category filter: {hotels.count()}")
        
        # Apply amenities filter - FIXED: Use custom filtering for JSON arrays
        if amenities:
            print(f"🔍 DEBUG [FilterHotelsView]: Filtering amenities: {amenities}")
            
            # Clean and normalize amenities
            clean_amenities = []
            for amenity in amenities:
                if amenity and amenity.strip():
                    # Normalize: lowercase, replace spaces with underscores
                    clean_amenity = amenity.strip().lower().replace(' ', '_')
                    clean_amenities.append(clean_amenity)
            
            print(f"🔍 DEBUG [FilterHotelsView]: Cleaned amenities: {clean_amenities}")
            
            if clean_amenities:
                # We need to manually filter because Django's JSONField queries are tricky
                filtered_hotels = []
                
                for hotel in hotels:
                    hotel_has_all_amenities = True
                    
                    if hotel.amenities and isinstance(hotel.amenities, list):
                        hotel_amenities_lower = []
                        for hotel_amenity in hotel.amenities:
                            if isinstance(hotel_amenity, str):
                                # Normalize hotel amenity for comparison
                                normalized_hotel_amenity = hotel_amenity.strip().lower().replace(' ', '_')
                                hotel_amenities_lower.append(normalized_hotel_amenity)
                        
                        # Check if hotel has ALL selected amenities
                        for selected_amenity in clean_amenities:
                            if selected_amenity not in hotel_amenities_lower:
                                hotel_has_all_amenities = False
                                break
                        
                        if hotel_has_all_amenities:
                            filtered_hotels.append(hotel)
                    else:
                        # Hotel has no amenities, can't match any
                        continue
                
                # Create a new queryset from filtered hotels
                hotel_ids = [h.id for h in filtered_hotels]
                hotels = hotels.filter(id__in=hotel_ids)
                
                print(f"🔍 DEBUG [FilterHotelsView]: After amenities filter: {hotels.count()}")
        
        # Order by price (unless searching)
        if not search_query:
            hotels = hotels.order_by('price_per_night')
        
        # Prepare hotel data for JSON response
        hotel_data = []
        for hotel in hotels:
            image_url = ''
            if hotel.image and hasattr(hotel.image, 'url'):
                try:
                    image_url = hotel.image.url
                except:
                    image_url = ''
            
            maps_query = f"{hotel.name} {hotel.address} {destination.name} Myanmar"
            
            # Get amenities as list for display
            hotel_amenities_display = []
            if hotel.amenities:
                if isinstance(hotel.amenities, list):
                    hotel_amenities_display = [str(a).replace('_', ' ').title() for a in hotel.amenities if a]
                elif isinstance(hotel.amenities, str):
                    try:
                        parsed = json.loads(hotel.amenities)
                        if isinstance(parsed, list):
                            hotel_amenities_display = [str(a).replace('_', ' ').title() for a in parsed if a]
                        else:
                            hotel_amenities_display = [hotel.amenities.replace('_', ' ').title()]
                    except:
                        hotel_amenities_display = [hotel.amenities.replace('_', ' ').title()]
            
            hotel_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'address': hotel.address,
                'price': float(hotel.price_per_night),
                'price_display': hotel.price_in_mmk(),
                'rating': float(hotel.rating),
                'review_count': hotel.review_count,
                'category': hotel.category,
                'category_display': hotel.get_category_display(),
                'amenities': hotel_amenities_display[:8],
                'amenities_count': len(hotel_amenities_display),
                'description': hotel.description[:100] + '...' if hotel.description and len(hotel.description) > 100 else (hotel.description or ''),
                'image_url': image_url,
                'maps_query': maps_query,
                'iframe_url': f"https://maps.google.com/maps?width=100%&height=300&hl=en&q={urllib.parse.quote(maps_query)}&t=&z=14&ie=UTF8&iwloc=B&output=embed",
                'phone': hotel.phone_number or '',
                'has_image': bool(image_url),
            })
        
        print(f"🔍 DEBUG [FilterHotelsView]: Found {len(hotel_data)} hotels")
        
        return JsonResponse({
            'success': True,
            'hotels': hotel_data,
            'count': len(hotel_data),
            'filters': {
                'category': category,
                'amenities': amenities,
                'search': search_query,
            }
        })
# ========== SAVE HOTEL VIEW ==========
# ========== SAVE HOTEL VIEW ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

class SaveHotelView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        hotel_id = request.POST.get('hotel_id')
        
        if hotel_id:
            try:
                hotel = Hotel.objects.get(id=hotel_id)
                trip.selected_hotel = hotel
                trip.accommodation_type = hotel.category
                trip.save()
                
                # Build redirect URL to MAIN PLAN PAGE
                redirect_url = reverse('planner:plan')
                params = []
                
                # Include origin and destination
                if trip.origin:
                    params.append(f'origin_id={trip.origin.id}')
                    params.append(f'origin_name={urllib.parse.quote(trip.origin.name)}')
                
                if trip.destination:
                    params.append(f'destination_id={trip.destination.id}')
                    params.append(f'destination_name={urllib.parse.quote(trip.destination.name)}')
                
                # Add hotel
                params.append(f'hotel_id={hotel_id}')
                params.append(f'hotel_name={urllib.parse.quote(hotel.name)}')
                
                # Add dates
                if trip.start_date:
                    params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
                if trip.end_date:
                    params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
                
                # Add travelers
                params.append(f'travelers={trip.travelers}')
                
                # Check if transport exists and include it
                if trip.selected_transport:
                    transport_data = trip.selected_transport
                    if transport_data.get('id'):
                        params.append(f'transport_id={transport_data.get("id")}')
                        params.append(f'transport_type={transport_data.get("type", "")}')
                        params.append(f'transport_name={urllib.parse.quote(transport_data.get("name", ""))}')
                
                # Build final URL
                if params:
                    redirect_url += '?' + '&'.join(params)
                
                # Return JSON response for AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Hotel {hotel.name} selected successfully!',
                        'hotel_name': hotel.name,
                        'redirect_url': redirect_url  # Send back to plan page
                    })
                else:
                    messages.success(request, f'Hotel {hotel.name} selected successfully!')
                    return redirect(redirect_url)
                
            except Hotel.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Hotel not found.'
                    })
                else:
                    messages.error(request, 'Hotel not found.')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Please select a hotel'
                })
            else:
                messages.error(request, 'Please select a hotel')
        
        return redirect('planner:select_hotel_map', trip_id=trip.id)

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

class SaveRoomSelectionView(LoginRequiredMixin, View):
    """Save room selection (called from AJAX)"""
    
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            room_ids = data.get('room_ids', [])
            
            if not room_ids:
                return JsonResponse({'success': False, 'error': 'No rooms selected'})
            
            # Validate availability again
            hotel = trip.selected_hotel
            if not hotel:
                return JsonResponse({'success': False, 'error': 'No hotel selected'})
            
            check_in = trip.start_date
            check_out = trip.end_date
            
            # Check room availability
            from .models_room import Room, RoomBooking
            available_room_ids = []
            for room_id in room_ids:
                if hotel.check_room_availability(room_id, check_in, check_out):
                    available_room_ids.append(str(room_id))
            
            invalid_rooms = [rid for rid in room_ids if str(rid) not in available_room_ids]
            
            if invalid_rooms:
                return JsonResponse({
                    'success': False, 
                    'error': 'Some rooms are no longer available',
                    'invalid_rooms': invalid_rooms
                })
            
            # Calculate price
            rooms = Room.objects.filter(id__in=room_ids)
            nights = trip.calculate_nights()
            total_price = 0
            room_details = []
            
            for room in rooms:
                price_per_night = room.get_price_per_night()
                room_total = price_per_night * nights
                total_price += room_total
                room_details.append({
                    'id': room.id,
                    'room_number': room.room_number,
                    'room_type': room.room_type.name,
                    'price_per_night': float(price_per_night),
                    'total': float(room_total),
                    'floor': room.floor,
                    'bed_type': room.bed_type
                })
            
            # Save to trip
            trip.selected_rooms = {
                'room_ids': room_ids,
                'total_price': float(total_price),
                'room_details': room_details,
                'is_temporary': True
            }
            trip.save()
            
            # Build redirect URL to MAIN PLAN PAGE
            redirect_url = reverse('planner:plan')
            params = []
            
            # Include origin and destination
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={urllib.parse.quote(trip.origin.name)}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={urllib.parse.quote(trip.destination.name)}')
            
            # Add hotel
            if trip.selected_hotel:
                params.append(f'hotel_id={trip.selected_hotel.id}')
                params.append(f'hotel_name={urllib.parse.quote(trip.selected_hotel.name)}')
            
            # Add dates
            if trip.start_date:
                params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
            if trip.end_date:
                params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
            
            # Add travelers
            params.append(f'travelers={trip.travelers}')
            
            # Check if transport exists and include it
            if trip.selected_transport:
                transport_data = trip.selected_transport
                if transport_data.get('id'):
                    params.append(f'transport_id={transport_data.get("id")}')
                    params.append(f'transport_type={transport_data.get("type", "")}')
                    params.append(f'transport_name={urllib.parse.quote(transport_data.get("name", ""))}')
            
            # Build final URL
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return JsonResponse({
                'success': True,
                'message': f'{len(room_ids)} room(s) selected',
                'total_price': float(total_price),
                'room_details': room_details,
                'redirect_url': redirect_url  # Send back to plan page
            })
            
        except Exception as e:
            print(f"Error in SaveRoomSelectionView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})


# ========== REAL HOTELS VIEW ==========
class GetRealHotelsView(LoginRequiredMixin, View):
    def get(self, request):
        destination_id = request.GET.get('destination_id')
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        
        try:
            if latitude and longitude:
                lat = float(latitude)
                lng = float(longitude)
            elif destination_id:
                destination = get_object_or_404(Destination, id=destination_id)
                if destination.latitude and destination.longitude:
                    lat = float(destination.latitude)
                    lng = float(destination.longitude)
                else:
                    geocoded = real_hotels_service.geocode_location(
                        f"{destination.name}, {destination.region}, Myanmar"
                    )
                    if geocoded:
                        lat = geocoded['latitude']
                        lng = geocoded['longitude']
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Could not determine location'
                        })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing location information'
                })
            
            real_hotels = real_hotels_service.search_nearby_hotels(lat, lng)
            
            return JsonResponse({
                'success': True,
                'hotels': real_hotels,
                'count': len(real_hotels),
                'location': {'lat': lat, 'lng': lng}
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# ========== SIMPLE REDIRECT VIEWS ==========
class SelectHotelView(LoginRequiredMixin, View):
    def get(self, request, trip_id):
        return redirect('planner:select_hotel_map', trip_id=trip_id)


class SelectTransportCategoryView(LoginRequiredMixin, View):
    template_name = 'planner/transport_category.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        context = {'trip': trip}
        return render(request, self.template_name, context)


# ========== SAVE TRANSPORT VIEW ==========
class SaveTransportView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        
        try:
            trip.transportation_preference = transport_type
            
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport_name = f"{transport.airline} Flight {transport.flight_number}"
                price = transport.price_in_mmk()
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = f"{transport.company} Bus"
                price = transport.price_in_mmk()
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                transport_name = f"{transport.company} - {transport.car_model}"
                price = transport.price_in_mmk() if hasattr(transport, 'price_in_mmk') else transport.price_per_day
            else:
                messages.error(request, 'Invalid transport type.')
                return redirect('planner:select_transport_category', trip_id=trip.id)
            
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
                'price': price
            }
            trip.save()
            
            # Build redirect URL to MAIN PLAN PAGE
            redirect_url = reverse('planner:plan')  # Changed from plan_selection to plan
            params = []
            
            # CRITICAL: Always include origin and destination
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={trip.origin.name}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={trip.destination.name}')
            
            # IMPORTANT: Check if hotel already exists and include it
            if trip.selected_hotel:
                params.append(f'hotel_id={trip.selected_hotel.id}')
                params.append(f'hotel_name={trip.selected_hotel.name}')
            
            # Add transport
            params.append(f'transport_id={transport_id}')
            params.append(f'transport_type={transport_type}')
            params.append(f'transport_name={transport_name}')
            
            # Add dates
            if trip.start_date:
                params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
            if trip.end_date:
                params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
            
            # Add travelers
            params.append(f'travelers={trip.travelers}')
            
            # Build final URL
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return redirect(redirect_url)  # Redirect to main plan page
            
        except Exception as e:
            messages.error(request, f'Error saving transport: {str(e)}')
            return redirect('planner:select_transport_category', trip_id=trip.id)

# ========== SELECT TRANSPORT VIEW ==========
# ========== SELECT TRANSPORT VIEW ==========
# ========== SELECT TRANSPORT VIEW ==========
class SelectTransportView(LoginRequiredMixin, View):
    template_name = 'planner/transport_list.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        transport_class = request.GET.get('transport_class', 'all')
        
        # Check if trip has dates
        if not trip.start_date:
            messages.error(request, 'Please select travel dates first.')
            return redirect('planner:plan')
        
        travel_date = trip.start_date
        
        transport_items = []
        error_message = None
        
        if transport_type == 'flight':
            # Check if origin and destination exist
            if not trip.origin or not trip.destination:
                error_message = "Please select both origin and destination."
            # Check if both have airports
            elif not self.check_has_airport(trip.origin) or not self.check_has_airport(trip.destination):
                error_message = f"✈️ Air travel not available between these locations. Please check if both {trip.origin.name} and {trip.destination.name} have airports."
            else:
                # Get flights for this specific date
                transport_items = self.get_flights_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    error_message = f"⚠️ No flights available on {travel_date.strftime('%B %d, %Y')}. Try a different date or check back later."
            
        elif transport_type == 'bus':
            if not trip.origin or not trip.destination:
                error_message = "Please select both origin and destination."
            else:
                # Get buses for this specific date
                transport_items = self.get_buses_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    # Check if route exists but no schedules
                    route_exists = BusService.objects.filter(
                        departure=trip.origin,
                        arrival=trip.destination,
                        is_active=True
                    ).exists()
                    
                    if route_exists:
                        error_message = f"🚌 No bus schedules available for {travel_date.strftime('%B %d')}. Schedules might be sold out or not yet loaded."
                    else:
                        error_message = f"🚌 No direct bus route found from {trip.origin.name} to {trip.destination.name}."
            
        elif transport_type == 'car':
            if not trip.origin:
                error_message = "Please select an origin city."
            else:
                # Get cars available on this date
                transport_items = self.get_cars_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    error_message = f"🚗 No cars available for rent in {trip.origin.name} on {travel_date.strftime('%B %d')}. Try a different date or city."
        
        # If no transport available and no error message yet, set generic message
        if not transport_items and not error_message:
            error_message = f"No {transport_type} options available for {travel_date.strftime('%B %d, %Y')}. Please try a different date or transport type."
        
        # DEBUG: Show what we found
        print(f"DEBUG: Transport Type: {transport_type}")
        print(f"DEBUG: Found {len(transport_items)} items")
        print(f"DEBUG: Error Message: {error_message}")
        
        context = {
            'trip': trip,
            'transport_type': transport_type,
            'transport_items': transport_items,
            'transport_class': transport_class,
            'travel_date': travel_date,
            'error_message': error_message,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, trip_id):
        """Handle transport selection directly (for cars and simple booking)"""
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        schedule_id = request.POST.get('schedule_id')
        
        print(f"DEBUG SelectTransportView.post: transport_type={transport_type}, transport_id={transport_id}")
        
        try:
            if transport_type == 'car':
                # Car rental - no seat selection needed
                car = get_object_or_404(CarRental, id=transport_id)
                
                if schedule_id:
                    schedule = get_object_or_404(TransportSchedule, id=schedule_id)
                    price_per_day = float(schedule.price)
                else:
                    price_per_day = float(car.price_per_day)
                
                # Calculate total price based on trip duration
                nights = trip.calculate_nights()
                days = nights + 1 if nights > 0 else 1
                total_price = price_per_day * days
                
                trip.transportation_preference = 'car'
                trip.selected_transport = {
                    'type': 'car',
                    'id': transport_id,
                    'schedule_id': schedule_id,
                    'name': f"{car.company} - {car.car_model}",
                    'price': total_price,
                    'travel_date': trip.start_date.strftime('%Y-%m-%d'),
                    'booking_details': {
                        'company': car.company,
                        'car_model': car.car_model,
                        'car_type': car.get_car_type_display(),
                        'pickup_location': trip.origin.name if trip.origin else 'Not specified',
                        'travel_date': trip.start_date.strftime('%Y-%m-%d'),
                        'duration_days': days,
                        'price_per_day': price_per_day,
                        'total_price': total_price,
                        'status': 'CONFIRMED',
                        'confirmed_at': timezone.now().isoformat(),
                    },
                    'is_temporary': False,
                    'needs_confirmation': False,
                }
                trip.save()
                
                print(f"DEBUG: Car rental saved. Price: {total_price}")
                
                messages.success(request, f'🚗 Car selected: {car.company} - {car.car_model}')
                
                # For car rental, redirect directly to plan selection page
                return redirect('planner:plan_selection', trip_id=trip.id)
                
            elif transport_type in ['flight', 'bus']:
                # Get the transport object
                if transport_type == 'flight':
                    transport = get_object_or_404(Flight, id=transport_id)
                    price = float(transport.price)
                    transport_name = f"{transport.airline} Flight {transport.flight_number}"
                else:  # bus
                    transport = get_object_or_404(BusService, id=transport_id)
                    price = float(transport.price)
                    transport_name = f"{transport.company} Bus"
                
                # Calculate total price for all travelers
                total_price = price * trip.travelers
                
                # Save transport data with price
                trip.transportation_preference = transport_type
                trip.selected_transport = {
                    'type': transport_type,
                    'id': transport_id,
                    'schedule_id': schedule_id,
                    'name': transport_name,
                    'price': total_price,
                    'travel_date': trip.start_date.strftime('%Y-%m-%d'),
                    'booking_details': {
                        'transport_name': transport_name,
                        'travel_date': trip.start_date.strftime('%Y-%m-%d'),
                        'travelers': trip.travelers,
                        'price_per_seat': price,
                        'total_price': total_price,
                        'status': 'SELECTED',
                        'selected_at': timezone.now().isoformat(),
                    },
                    'is_temporary': True,
                    'needs_confirmation': True,
                }
                trip.save()
                
                print(f"DEBUG: {transport_type} saved. Total price: {total_price}")
                
                # Redirect to seat selection
                print(f"DEBUG: Redirecting to seat selection for {transport_type}")
                return redirect('planner:select_seats', 
                              trip_id=trip.id, 
                              transport_id=transport_id,
                              type=transport_type)
                
        except Exception as e:
            print(f"ERROR in SelectTransportView.post: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error selecting transport: {str(e)}')
            return redirect('planner:select_transport', trip_id=trip.id, 
                          type=transport_type, transport_class='all')
    
    def check_has_airport(self, destination):
        """Check if a destination has an airport using the model method"""
        return destination.has_airport() if destination else False
    
    def get_flights_for_date(self, trip, travel_date, transport_class):
        """Get flights available for specific date"""
        # Get schedules for this date
        flight_schedules = TransportSchedule.objects.filter(
            transport_type='flight',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers
        )
        
        print(f"DEBUG: Found {flight_schedules.count()} flight schedules for {travel_date}")
        
        # Get actual flight objects
        flight_ids = flight_schedules.values_list('transport_id', flat=True)
        flights = Flight.objects.filter(
            id__in=flight_ids,
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        print(f"DEBUG: Found {flights.count()} flights for route {trip.origin.name} → {trip.destination.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            flights = flights.filter(category=transport_class)
        
        # Add schedule info to each flight
        transport_items = []
        for flight in flights:
            schedule = flight_schedules.filter(transport_id=flight.id).first()
            if schedule:
                # Create flight item with schedule data
                flight_item = flight
                flight_item.schedule_price = schedule.price
                flight_item.schedule_available_seats = schedule.available_seats
                flight_item.schedule_date = schedule.travel_date
                flight_item.schedule_id = schedule.id
                transport_items.append(flight_item)
                print(f"DEBUG: Added flight {flight.airline.name} {flight.flight_number} with {schedule.available_seats} seats")
        
        return transport_items
    
    def get_buses_for_date(self, trip, travel_date, transport_class):
        """Get buses available for specific date"""
        # Get schedules for this date
        bus_schedules = TransportSchedule.objects.filter(
            transport_type='bus',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers
        )
        
        print(f"DEBUG: Found {bus_schedules.count()} bus schedules for {travel_date}")
        
        # Get actual bus objects
        bus_ids = bus_schedules.values_list('transport_id', flat=True)
        buses = BusService.objects.filter(
            id__in=bus_ids,
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        print(f"DEBUG: Found {buses.count()} buses for route {trip.origin.name} → {trip.destination.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            if transport_class == 'low':
                buses = buses.filter(bus_type='standard')
            elif transport_class == 'medium':
                buses = buses.filter(bus_type='vip')
            elif transport_class == 'high':
                buses = buses.filter(bus_type='luxury')
        
        # Add schedule info to each bus
        transport_items = []
        for bus in buses:
            schedule = bus_schedules.filter(transport_id=bus.id).first()
            if schedule:
                bus.schedule_price = schedule.price
                bus.schedule_available_seats = schedule.available_seats
                bus.schedule_date = schedule.travel_date
                bus.schedule_id = schedule.id
                transport_items.append(bus)
                print(f"DEBUG: Added bus {bus.company} with {schedule.available_seats} seats")
        
        return transport_items
    
    def get_cars_for_date(self, trip, travel_date, transport_class):
        """Get cars available for specific date"""
        # Get schedules for this date
        car_schedules = TransportSchedule.objects.filter(
            transport_type='car',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers
        )
        
        print(f"DEBUG: Found {car_schedules.count()} car schedules for {travel_date}")
        
        # Get actual car objects
        car_ids = car_schedules.values_list('transport_id', flat=True)
        cars = CarRental.objects.filter(
            id__in=car_ids,
            location=trip.origin,
            is_available=True
        )
        
        print(f"DEBUG: Found {cars.count()} cars in {trip.origin.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            if transport_class == 'low':
                cars = cars.filter(car_type='economy')
            elif transport_class == 'medium':
                cars = cars.filter(car_type='suv')
            elif transport_class == 'high':
                cars = cars.filter(car_type='luxury')
        
        # Add schedule info to each car
        transport_items = []
        for car in cars:
            schedule = car_schedules.filter(transport_id=car.id).first()
            if schedule:
                car.schedule_price = schedule.price
                car.schedule_available_seats = schedule.available_seats
                car.schedule_date = schedule.travel_date
                car.schedule_id = schedule.id
                transport_items.append(car)
                print(f"DEBUG: Added car {car.company} {car.car_model} with {schedule.available_seats} seats")
        
        return transport_items
class DestinationListView(View):
    """Browse destinations - SHOW ONLY CITIES AND TOWNS (NO REGIONS, NO ATTRACTIONS)"""
    template_name = 'planner/destinations.html'

    def get(self, request):
        # Get filter parameters
        region_filter = request.GET.get('region', 'all')
        type_filter = request.GET.get('type', 'all')
        search_query = request.GET.get('search', '')

        # IMPORTANT: Get ONLY cities and towns (NO regions, NO attractions)
        destinations = Destination.objects.filter(
            is_active=True,
            type__in=['city', 'town']  # ← ONLY cities and towns, NO regions!
        )
        
        # Also exclude anything that has a parent (attractions have parents)
        destinations = destinations.filter(parent__isnull=True)
        
        # Explicitly exclude attraction type (just to be safe)
        destinations = destinations.exclude(type='attraction')
        
        # Explicitly exclude region type (double safety)
        destinations = destinations.exclude(type='region')
        
        # Exclude by name patterns (backup for any misclassified attractions)
        exclude_keywords = ['Pagoda', 'Temple', 'Monastery', 'Market', 'Lake', 'Beach', 
                           'Falls', 'Cave', 'Bridge', 'Palace', 'Village', 'Island',
                           'Factory', 'Garden', 'Museum']
        
        for keyword in exclude_keywords:
            destinations = destinations.exclude(name__icontains=keyword)

        # Apply region filter
        if region_filter != 'all':
            destinations = destinations.filter(region__iexact=region_filter)

        # Apply type filter
        if type_filter != 'all':
            if type_filter in ['city', 'town']:  # ← Only city and town in filter dropdown
                destinations = destinations.filter(type=type_filter)

        # Apply search filter
        if search_query:
            destinations = destinations.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(region__icontains=search_query)
            )

        # Debug: Print what we're showing
        print(f"\n🔍 DESTINATIONS PAGE - Showing ONLY cities/towns:")
        for d in destinations:
            print(f"  - {d.name} (Type: {d.type}, Region: {d.region})")
        print(f"  Total: {destinations.count()}\n")

        # Group by region
        destinations_by_region = {}
        for destination in destinations.order_by('region', 'name'):
            destinations_by_region.setdefault(destination.region, []).append(destination)

        # Get all unique regions from filtered destinations
        all_regions = (
            destinations
            .values_list('region', flat=True)
            .distinct()
            .order_by('region')
        )

        context = {
            'destinations_by_region': destinations_by_region,
            'all_regions': all_regions,
            'all_types': ['city', 'town'],  # ← Only city and town in filter dropdown
            'selected_region': region_filter,
            'selected_type': type_filter,
            'search_query': search_query,
            'destinations_count': destinations.count(),
            'user': request.user,
        }

        return render(request, self.template_name, context)
# ========== SEARCH REAL HOTELS VIEW ==========
class SearchRealHotelsView(LoginRequiredMixin, View):
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        try:
            if destination.latitude and destination.longitude:
                lat = float(destination.latitude)
                lng = float(destination.longitude)
            else:
                geocoded = real_hotels_service.geocode_location(f"{destination.name}, Myanmar")
                if geocoded:
                    lat = geocoded['latitude']
                    lng = geocoded['longitude']
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Destination coordinates not available'
                    })
            
            real_hotels = real_hotels_service.search_nearby_hotels(lat, lng)
            
            return JsonResponse({
                'success': True,
                'hotels': real_hotels,
                'count': len(real_hotels),
                'location': f'{destination.name}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# ========== BOOK REAL HOTEL VIEW ==========
class BookRealHotelView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            hotel_data = data.get('hotel_data')
            
            if not hotel_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No hotel data provided'
                })
            
            booking_id = f"RB{int(timezone.now().timestamp())}"
            
            messages.success(
                request, 
                f"Simulated booking successful for {hotel_data.get('name', 'Hotel')}! "
                f"Booking ID: {booking_id}"
            )
            
            return JsonResponse({
                'success': True,
                'booking_id': booking_id,
                'message': 'Simulated booking successful',
                'hotel_name': hotel_data.get('name'),
                'total_price': hotel_data.get('price', 0) * trip.calculate_nights()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# ========== CLEAR TRIP VIEW ==========
class ClearTripDataView(LoginRequiredMixin, View):
    def get(self, request):
        # Clear ANY trip-related data from session
        session_keys = list(request.session.keys())
        
        # List of session keys to clear
        keys_to_clear = [
            'selected_hotel',
            'selected_hotel_id', 
            'selected_hotel_name',
            'selected_transport',
            'selected_transport_id',
            'selected_transport_type',
            'selected_transport_name',
            'hotel_search_results',
            'transport_search_results',
            'current_trip_id',
            'trip_origin',
            'trip_destination',
            'trip_start_date', 
            'trip_end_date',
            'trip_travelers',
            'trip_budget',
        ]
        
        # Also clear any keys that start with these prefixes
        for key in session_keys:
            if (key.startswith('ai_plans_') or 
                key.startswith('selected_plan_') or
                key.startswith('plan_details_') or
                key in keys_to_clear):
                del request.session[key]
        
        # Clear any draft trips from database
        TripPlan.objects.filter(
            user=request.user,
            status__in=['draft', 'planning']
        ).delete()
        
        request.session.modified = True
        messages.success(request, 'All trip data has been cleared. You can start a new trip.')
        return redirect('planner:plan')


# ========== NEW VIEWS FOR PLAN SELECTION ==========

# ========== NEW VIEWS FOR PLAN SELECTION ==========

# ========== NEW VIEWS FOR PLAN SELECTION ==========

# In C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Update the PlanSelectionView class:


from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from .models import TripPlan
# ========== PLAN SELECTION VIEW ==========

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from planner.models import TripPlan, BookedSeat, TransportSchedule

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import TripPlan, BookedSeat, TransportSchedule


# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py



    # ========== KEEP ALL YOUR EXISTING METHODS HERE ==========
    # generate_ai_plans, get_cultural_highlights, get_adventure_highlights, 
    # get_relaxed_highlights, generate_cultural_itinerary, 
    # generate_adventure_itinerary, generate_relaxed_itinerary, 
    # calculate_date - ALL THESE METHODS REMAIN THE SAME
    # (I'm not including them here to save space, but keep them exactly as in your original code)

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

class PlanSelectionView(LoginRequiredMixin, View):
    template_name = 'planner/plan_selection.html'

    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id)

        # ================= PERMISSION =================
        if not request.user.is_staff and trip.user != request.user:
            return HttpResponseForbidden("You do not have permission to view this trip")

        # ================= CLEAR OLD SESSION =================
        for key in list(request.session.keys()):
            if key.startswith('selected_plan_') and key != f'selected_plan_{trip_id}':
                del request.session[key]

        # ================= DAYS / NIGHTS =================
        try:
            if hasattr(trip, 'calculate_nights'):
                nights = trip.calculate_nights()
            else:
                nights = (trip.end_date - trip.start_date).days
        except:
            nights = 1

        if nights <= 0:
            nights = 1

        days = nights + 1

        # ================= BUDGET =================
        budget = getattr(trip, 'budget', 500000)

        # ================= AI PLANS =================
        session_key = f'ai_plans_{trip_id}'
        plans = request.session.get(session_key, [])

        if not plans:
            plans = self.generate_ai_plans(trip, days, budget)
            request.session[session_key] = plans
            request.session.modified = True

        # ================= SELECTED PLAN =================
        selected_plan_id = request.session.get(f'selected_plan_{trip_id}')

        if hasattr(trip, 'selected_plan') and trip.selected_plan:
            selected_plan_id = trip.selected_plan
            request.session[f'selected_plan_{trip_id}'] = selected_plan_id

        selected_plan = None

        if selected_plan_id:
            try:
                selected_plan_id = int(selected_plan_id)
                selected_plan = next(
                    (p for p in plans if p.get('id') == selected_plan_id),
                    None
                )
            except:
                selected_plan = None

            if not selected_plan:
                request.session.pop(f'selected_plan_{trip_id}', None)

        for plan in plans:
            plan['is_selected'] = (str(plan.get('id')) == str(selected_plan_id))

        # ================= HOTEL AND ROOMS =================
        selected_hotel = getattr(trip, 'selected_hotel', None)

        # ROOM COSTS ONLY
        room_total_cost_numeric = 0
        room_total_cost_mmk = "No rooms selected"
        room_details = []

        if trip.selected_rooms and trip.selected_rooms.get('room_details'):
            room_details = trip.selected_rooms.get('room_details', [])
            
            # Recalculate total to ensure accuracy
            recalculated_total = 0
            for room in room_details:
                price_per_night = float(room.get('price_per_night', 0))
                room_total = price_per_night * nights
                recalculated_total += room_total
                room['total'] = room_total
            
            room_total_cost_numeric = recalculated_total
            room_total_cost_mmk = f"{room_total_cost_numeric:,.0f} MMK"

        # ================= TRANSPORT =================
        selected_transport = None
        try:
            if isinstance(trip.selected_transport, dict):
                selected_transport = trip.selected_transport
        except:
            selected_transport = None

        transport_cost_numeric = 0
        transport_cost_mmk = "Not selected"
        has_pending_seats = False

        if selected_transport:
            try:
                transport_type = selected_transport.get('type', '')
                booking_details = selected_transport.get('booking_details', {})

                # ========= BUS / FLIGHT =========
                if transport_type in ['bus', 'flight']:
                    total_price = booking_details.get('total_price')
                    
                    if total_price:
                        transport_cost_numeric = float(total_price)
                        transport_cost_mmk = f"{transport_cost_numeric:,.0f} MMK"
                        has_pending_seats = False
                    else:
                        seats = selected_transport.get('seats', [])
                        seat_count = len(seats)
                        price_per_seat = selected_transport.get('price')

                        if price_per_seat and seat_count > 0:
                            transport_cost_numeric = float(price_per_seat) * seat_count
                            transport_cost_mmk = f"{transport_cost_numeric:,.0f} MMK"
                            has_pending_seats = True
                        else:
                            transport_cost_mmk = "Pending confirmation"
                            has_pending_seats = True

                # ========= CAR =========
                elif transport_type == 'car':
                    total_price = booking_details.get('total_price')
                    
                    if total_price:
                        transport_cost_numeric = float(total_price)
                    else:
                        price_per_day = float(booking_details.get('price_per_day', 0))
                        duration = int(booking_details.get('duration_days', 1))
                        transport_cost_numeric = price_per_day * duration

                    if transport_cost_numeric > 0:
                        transport_cost_mmk = f"{transport_cost_numeric:,.0f} MMK"
                    else:
                        transport_cost_mmk = "Price not available"

                # ========= OTHER =========
                else:
                    price = selected_transport.get('price')
                    if price:
                        transport_cost_numeric = float(price)
                        transport_cost_mmk = f"{transport_cost_numeric:,.0f} MMK"
                    else:
                        transport_cost_mmk = "Price not available"

            except Exception as e:
                print("Transport Error:", e)
                transport_cost_mmk = "Error calculating"

        # ================= TOTAL (Rooms + Transport ONLY) =================
        total_combined_cost_numeric = (
            room_total_cost_numeric + 
            transport_cost_numeric
        )

        if total_combined_cost_numeric > 0:
            total_combined_cost_mmk = f"{total_combined_cost_numeric:,.0f} MMK"
        else:
            total_combined_cost_mmk = "-"

        # ================= CONTEXT =================
        context = {
            'trip': trip,
            'plans': plans,
            'destination': trip.destination,

            'days': days,
            'nights': nights,

            'start_date': trip.start_date.strftime('%Y-%m-%d') if trip.start_date else '',
            'end_date': trip.end_date.strftime('%Y-%m-%d') if trip.end_date else '',

            'travelers': getattr(trip, 'travelers', 1),

            'selected_hotel': selected_hotel,
            'selected_transport': selected_transport,
            'room_details': room_details,

            'plan_selected': bool(selected_plan_id),

            'selected_plan': selected_plan,
            'selected_plan_id': selected_plan_id,

            'trip_budget': budget,

            'has_pending_seats': has_pending_seats,

            # ROOM COSTS
            'room_total_cost_mmk': room_total_cost_mmk,
            'room_total_cost_numeric': room_total_cost_numeric,

            # TRANSPORT
            'transport_cost_mmk': transport_cost_mmk,
            'transport_cost_numeric': transport_cost_numeric,

            # REMOVED: destination_cost_mmk and destination_cost_numeric

            # TOTAL (Rooms + Transport)
            'total_combined_cost_mmk': total_combined_cost_mmk,
            'total_combined_cost_numeric': total_combined_cost_numeric,
        }

        return render(request, self.template_name, context)

    # ========== KEEP ALL THE REST OF YOUR METHODS EXACTLY AS THEY ARE ==========
    # generate_ai_plans, get_cultural_highlights, get_adventure_highlights, 
    # get_relaxed_highlights, generate_cultural_itinerary, 
    # generate_adventure_itinerary, generate_relaxed_itinerary, 
    # calculate_date - ALL THESE METHODS REMAIN THE SAME
    # ========== KEEP ALL THE REST OF YOUR METHODS EXACTLY AS THEY ARE ==========
    # generate_ai_plans, get_cultural_highlights, get_adventure_highlights, 
    # get_relaxed_highlights, generate_cultural_itinerary, 
    # generate_adventure_itinerary, generate_relaxed_itinerary, 
    # calculate_date - ALL THESE METHODS REMAIN THE SAME

    # ========== KEEP ALL THE REST OF YOUR METHODS EXACTLY AS THEY ARE ==========
    # generate_ai_plans, get_cultural_highlights, get_adventure_highlights, 
    # get_relaxed_highlights, generate_cultural_itinerary, 
    # generate_adventure_itinerary, generate_relaxed_itinerary, 
    # calculate_date - ALL THESE METHODS REMAIN THE SAME
    def generate_ai_plans(self, trip, days, budget):
        """Generate AI travel plans based on trip details - WITHOUT Estimated Cost"""
        destination = trip.destination.name
        
        # Generate destination-specific highlights
        cultural_highlights = self.get_cultural_highlights(trip.destination)[:6]
        adventure_highlights = self.get_adventure_highlights(trip.destination)[:6]
        relaxed_highlights = self.get_relaxed_highlights(trip.destination)[:6]
        
        # Generate sample itineraries
        cultural_itinerary = self.generate_cultural_itinerary(trip, days)
        adventure_itinerary = self.generate_adventure_itinerary(trip, days)
        relaxed_itinerary = self.generate_relaxed_itinerary(trip, days)
        
        plans = [
            {
                'id': 1,
                'title': 'Cultural Explorer',
                'subtitle': 'Immerse in local traditions and heritage',
                'category': 'Cultural',
                'color': '#3498db',
                'icon': 'fas fa-landmark',
                'duration': f'{days} days',
                'budget_range': '$$$',
                'highlights': cultural_highlights,
                'days': cultural_itinerary,
                'sample_day': cultural_itinerary[0]['activities'][:3] if cultural_itinerary else [],
                'description': f'Perfect for history buffs and culture enthusiasts who want to immerse in {destination}\'s local traditions and heritage sites.',
                'is_selected': False,
                'popularity': 'Most Popular'
            },
            {
                'id': 2,
                'title': 'Adventure Seeker',
                'subtitle': 'Active exploration and new experiences',
                'category': 'Adventure',
                'color': '#2ecc71',
                'icon': 'fas fa-hiking',
                'duration': f'{days} days',
                'budget_range': '$$$$',
                'highlights': adventure_highlights,
                'days': adventure_itinerary,
                'sample_day': adventure_itinerary[0]['activities'][:3] if adventure_itinerary else [],
                'description': f'Ideal for active travelers who love outdoor activities, exploration, and trying new experiences in {destination}.',
                'is_selected': False,
                'popularity': 'Trending'
            },
            {
                'id': 3,
                'title': 'Relaxed Wanderer',
                'subtitle': 'Leisurely pace with ample relaxation',
                'category': 'Relaxation',
                'color': '#9b59b6',
                'icon': 'fas fa-spa',
                'duration': f'{days} days',
                'budget_range': '$$',
                'highlights': relaxed_highlights,
                'days': relaxed_itinerary,
                'sample_day': relaxed_itinerary[0]['activities'][:3] if relaxed_itinerary else [],
                'description': f'Best for those who prefer a leisurely pace with ample free time and relaxation activities in {destination}.',
                'is_selected': False,
                'popularity': 'Value'
            }
        ]
        
        return plans

    def get_cultural_highlights(self, destination):
        """Get destination-specific cultural highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Shwedagon Pagoda at sunrise',
                'Colonial architecture walking tour',
                'Traditional puppet show',
                'Local tea house experience',
                'Bogyoke Market shopping',
                'National Museum visit'
            ],
            'mandalay': [
                'Mandalay Palace tour',
                'Mandalay Hill sunset view',
                'Gold leaf making workshop',
                'Traditional marionette theater',
                'Kuthodaw Pagoda (World\'s largest book)',
                'U Bein Bridge at sunrise'
            ],
            'bagan': [
                'Temple sunrise hot air balloon',
                'Ancient temple exploration',
                'Lacquerware workshop visit',
                'Traditional horse cart ride',
                'Local village life experience',
                'Sunset at Buledi temple'
            ],
            'inle lake': [
                'Leg-rowing fishermen demonstration',
                'Floating village tour',
                'Traditional weaving workshop',
                'Phaung Daw Oo Pagoda visit',
                'Local market experience',
                'Stilt house village walk'
            ],
            'pyin oo lwin': [
                'Botanical gardens tour',
                'Colonial architecture walk',
                'Candy factory visit',
                'Local strawberry farm',
                'Waterfall visits',
                'Horse carriage ride'
            ]
        }
        
        # Find matching highlights
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights for other destinations
        return [
            'Local cultural sites visit',
            'Traditional craft workshop',
            'Historical landmark tour',
            'Local market exploration',
            'Cultural performance show',
            'Traditional cuisine tasting'
        ]

    def get_adventure_highlights(self, destination):
        """Get destination-specific adventure highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Circular train ride',
                'Kayaking on Kandawgyi Lake',
                'Street food walking tour',
                'Bicycle tour around city',
                'Yangon River cruise',
                'Night market exploration'
            ],
            'mandalay': [
                'Mandalay Hill hiking',
                'Mingun day trip by boat',
                'Motorbike tour around city',
                'Traditional cooking class',
                'Irrawaddy River activities',
                'Local market food adventure'
            ],
            'bagan': [
                'Hot air balloon ride',
                'E-bike temple exploration',
                'Sunrise cycling tour',
                'Irrawaddy River boat trip',
                'Temple climbing adventure',
                'Photography safari'
            ],
            'inle lake': [
                'Boat tour on Inle Lake',
                'Trekking to hill tribe villages',
                'Bamboo rafting experience',
                'Fishing with local methods',
                'Mountain biking around lake',
                'Sunrise boat photography'
            ],
            'ngapali': [
                'Beach relaxation',
                'Snorkeling adventure',
                'Sunset fishing trip',
                'Beach volleyball',
                'Local seafood tasting',
                'Coastal walk exploration'
            ]
        }
        
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights
        return [
            'Local hiking trails',
            'Outdoor exploration',
            'Traditional activities',
            'Nature walks',
            'Adventure sports',
            'Cultural adventures'
        ]

    def get_relaxed_highlights(self, destination):
        """Get destination-specific relaxed highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Spa and wellness sessions',
                'Leisurely park walks',
                'Café hopping downtown',
                'Sunset at Shwedagon',
                'Riverfront relaxation',
                'Art gallery visits'
            ],
            'mandalay': [
                'Spa treatments',
                'Royal garden walks',
                'Tea house relaxation',
                'Sunset viewing spots',
                'Cultural show evenings',
                'Leisurely shopping'
            ],
            'bagan': [
                'Temple view relaxation',
                'Sunset champagne viewing',
                'Poolside lounging',
                'Leisurely e-bike rides',
                'Traditional massage',
                'Stargazing nights'
            ],
            'inle lake': [
                'Lakeside relaxation',
                'Boat ride with tea',
                'Spa with lake view',
                'Leisurely village walks',
                'Sunset photography',
                'Traditional massage'
            ],
            'ngapali': [
                'Beachfront massage',
                'Sunset beach walks',
                'Hammock relaxation',
                'Seafood dining',
                'Beach yoga sessions',
                'Poolside lounging'
            ]
        }
        
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights
        return [
            'Spa and wellness sessions',
            'Leisurely nature walks',
            'Local café exploration',
            'Sunset photography spots',
            'Relaxation activities',
            'Cultural appreciation'
        ]

    def generate_cultural_itinerary(self, trip, days):
        """Generate cultural itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific activities
        activities_map = {
            'yangon': [
                {'time': '09:00 AM', 'title': 'Shwedagon Pagoda Visit', 'location': 'Shwedagon Pagoda', 'duration': '2 hours', 'description': 'Explore Myanmar\'s most sacred Buddhist pagoda', 'type': 'cultural'},
                {'time': '12:00 PM', 'title': 'Lunch at Feel Myanmar', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Authentic Myanmar cuisine experience', 'type': 'food'},
                {'time': '02:00 PM', 'title': 'Bogyoke Market', 'location': 'Pabedan Township', 'duration': '2 hours', 'description': 'Shop for local crafts, jewelry and souvenirs', 'type': 'shopping'},
                {'time': '05:00 PM', 'title': 'Colonial Architecture Tour', 'location': 'Downtown Yangon', 'duration': '1.5 hours', 'description': 'Walk through historic colonial buildings', 'type': 'cultural'}
            ],
            'mandalay': [
                {'time': '08:00 AM', 'title': 'Mandalay Palace', 'location': 'Mandalay Palace', 'duration': '2 hours', 'description': 'Explore the last royal palace of Myanmar', 'type': 'cultural'},
                {'time': '11:00 AM', 'title': 'Gold Leaf Workshop', 'location': 'Traditional Workshop', 'duration': '1.5 hours', 'description': 'See how traditional gold leaf is made', 'type': 'workshop'},
                {'time': '02:00 PM', 'title': 'Kuthodaw Pagoda', 'location': 'Mandalay Hill', 'duration': '2 hours', 'description': 'Visit the world\'s largest book', 'type': 'cultural'},
                {'time': '05:00 PM', 'title': 'Sunset at U Bein Bridge', 'location': 'Amarapura', 'duration': '1.5 hours', 'description': 'Watch sunset on the world\'s longest teak bridge', 'type': 'scenic'}
            ],
            'bagan': [
                {'time': '05:30 AM', 'title': 'Hot Air Balloon Sunrise', 'location': 'Bagan Plains', 'duration': '1 hour', 'description': 'Spectacular sunrise view over ancient temples', 'type': 'adventure'},
                {'time': '09:00 AM', 'title': 'Ananda Temple', 'location': 'Old Bagan', 'duration': '2 hours', 'description': 'Visit one of Bagan\'s most beautiful temples', 'type': 'cultural'},
                {'time': '01:00 PM', 'title': 'Lacquerware Workshop', 'location': 'Myinkaba Village', 'duration': '2 hours', 'description': 'Learn about traditional lacquerware making', 'type': 'workshop'},
                {'time': '05:00 PM', 'title': 'Sunset at Buledi', 'location': 'Bagan Archaeological Zone', 'duration': '1.5 hours', 'description': 'Climb a temple for panoramic sunset views', 'type': 'scenic'}
            ],
            'inle lake': [
                {'time': '07:00 AM', 'title': 'Leg-Rowing Fishermen', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'See unique leg-rowing fishing technique', 'type': 'cultural'},
                {'time': '10:00 AM', 'title': 'Floating Village Tour', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'Visit stilt-house villages on the lake', 'type': 'cultural'},
                {'time': '01:00 PM', 'title': 'Traditional Weaving', 'location': 'Inn Paw Khon Village', 'duration': '2 hours', 'description': 'Watch lotus and silk weaving process', 'type': 'workshop'},
                {'time': '04:00 PM', 'title': 'Phaung Daw Oo Pagoda', 'location': 'Inle Lake', 'duration': '1.5 hours', 'description': 'Visit the lake\'s most important pagoda', 'type': 'cultural'}
            ]
        }
        
        # Get activities for this destination
        base_activities = activities_map.get(destination_name, [
            {'time': '09:00 AM', 'title': 'Cultural Site Visit', 'location': 'Main Attraction', 'duration': '2 hours', 'description': f'Explore cultural sites in {trip.destination.name}', 'type': 'cultural'},
            {'time': '12:00 PM', 'title': 'Local Cuisine Lunch', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Taste authentic local dishes', 'type': 'food'},
            {'time': '02:00 PM', 'title': 'Market Exploration', 'location': 'Local Market', 'duration': '2 hours', 'description': 'Experience local market culture', 'type': 'shopping'},
            {'time': '05:00 PM', 'title': 'Sunset Viewing', 'location': 'Scenic Spot', 'duration': '1.5 hours', 'description': 'Enjoy beautiful sunset views', 'type': 'scenic'}
        ])
        
        # Add icons to activities
        icon_map = {
            'cultural': 'fas fa-landmark',
            'food': 'fas fa-utensils',
            'shopping': 'fas fa-shopping-bag',
            'workshop': 'fas fa-hammer',
            'scenic': 'fas fa-camera',
            'adventure': 'fas fa-hiking'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-star')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            # Vary activities slightly each day
            day_activities = []
            for i, activity in enumerate(base_activities):
                # Create a copy to modify
                activity_copy = activity.copy()
                
                # Vary times slightly for different days
                if day > 1:
                    time_parts = activity_copy['time'].split(' ')
                    hour_part = time_parts[0]
                    am_pm = time_parts[1] if len(time_parts) > 1 else 'AM'
                    hour = int(hour_part.split(':')[0])
                    
                    # Add 30 minutes for each subsequent day
                    hour_offset = (day - 1) * 0.5
                    new_hour = hour + hour_offset
                    
                    if new_hour >= 12 and am_pm == 'AM':
                        am_pm = 'PM'
                        if new_hour > 12:
                            new_hour -= 12
                    
                    activity_copy['time'] = f"{int(new_hour):02d}:{hour_part.split(':')[1]} {am_pm}"
                
                day_activities.append(activity_copy)
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary

    def generate_adventure_itinerary(self, trip, days):
        """Generate adventure itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific adventure activities
        activities_map = {
            'yangon': [
                {'time': '07:00 AM', 'title': 'Circular Train Ride', 'location': 'Yangon Central Station', 'duration': '3 hours', 'description': 'Experience local life on the circular railway', 'type': 'adventure'},
                {'time': '11:00 AM', 'title': 'Street Food Tour', 'location': 'Downtown Markets', 'duration': '2 hours', 'description': 'Taste authentic Yangon street food', 'type': 'food'},
                {'time': '02:00 PM', 'title': 'Kayaking on Lake', 'location': 'Kandawgyi Lake', 'duration': '2.5 hours', 'description': 'Paddle through scenic waters', 'type': 'water_sports'},
                {'time': '06:00 PM', 'title': 'Sunset Walking Tour', 'location': 'Downtown Area', 'duration': '2 hours', 'description': 'Explore the city at sunset', 'type': 'walking'}
            ],
            'mandalay': [
                {'time': '06:00 AM', 'title': 'Mandalay Hill Hike', 'location': 'Mandalay Hill', 'duration': '2 hours', 'description': 'Hike to the top for panoramic views', 'type': 'hiking'},
                {'time': '10:00 AM', 'title': 'Motorbike City Tour', 'location': 'Mandalay City', 'duration': '3 hours', 'description': 'Explore Mandalay on motorbike', 'type': 'adventure'},
                {'time': '02:00 PM', 'title': 'Mingun Boat Trip', 'location': 'Irrawaddy River', 'duration': '3 hours', 'description': 'Boat trip to Mingun ancient sites', 'type': 'boat'},
                {'time': '06:00 PM', 'title': 'Traditional Cooking Class', 'location': 'Local Kitchen', 'duration': '2 hours', 'description': 'Learn to cook Mandalay dishes', 'type': 'food'}
            ],
            'bagan': [
                {'time': '05:00 AM', 'title': 'Sunrise E-Bike Tour', 'location': 'Bagan Plains', 'duration': '3 hours', 'description': 'Explore temples by e-bike at sunrise', 'type': 'cycling'},
                {'time': '09:00 AM', 'title': 'Horse Cart Adventure', 'location': 'Ancient Temples', 'duration': '2 hours', 'description': 'Traditional horse cart temple tour', 'type': 'cultural'},
                {'time': '02:00 PM', 'title': 'Irrawaddy River Cruise', 'location': 'Irrawaddy River', 'duration': '2.5 hours', 'description': 'Boat trip on the mighty river', 'type': 'boat'},
                {'time': '06:00 PM', 'title': 'Sunset Temple Climb', 'location': 'Selected Temple', 'duration': '1.5 hours', 'description': 'Climb a temple for sunset views', 'type': 'hiking'}
            ],
            'inle lake': [
                {'time': '06:00 AM', 'title': 'Sunrise Boat Tour', 'location': 'Inle Lake', 'duration': '3 hours', 'description': 'Early morning boat tour of the lake', 'type': 'boat'},
                {'time': '10:00 AM', 'title': 'Trekking to Villages', 'location': 'Shan Hills', 'duration': '3 hours', 'description': 'Trek to remote hill tribe villages', 'type': 'hiking'},
                {'time': '02:00 PM', 'title': 'Bamboo Rafting', 'location': 'Streams near Lake', 'duration': '2 hours', 'description': 'Traditional bamboo raft experience', 'type': 'water_sports'},
                {'time': '05:00 PM', 'title': 'Bicycle Lake Tour', 'location': 'Lakeside Roads', 'duration': '2 hours', 'description': 'Cycle around the lake perimeter', 'type': 'cycling'}
            ]
        }
        
        base_activities = activities_map.get(destination_name, [
            {'time': '08:00 AM', 'title': 'Morning Exploration', 'location': 'Main Area', 'duration': '3 hours', 'description': f'Active exploration of {trip.destination.name}', 'type': 'adventure'},
            {'time': '12:00 PM', 'title': 'Local Food Experience', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Try local adventure foods', 'type': 'food'},
            {'time': '02:00 PM', 'title': 'Outdoor Activity', 'location': 'Natural Site', 'duration': '2.5 hours', 'description': 'Participate in local outdoor activities', 'type': 'adventure'},
            {'time': '05:00 PM', 'title': 'Evening Adventure', 'location': 'Scenic Location', 'duration': '2 hours', 'description': 'Evening adventure activities', 'type': 'adventure'}
        ])
        
        # Add icons
        icon_map = {
            'adventure': 'fas fa-hiking',
            'food': 'fas fa-utensils',
            'hiking': 'fas fa-mountain',
            'cycling': 'fas fa-bicycle',
            'boat': 'fas fa-ship',
            'water_sports': 'fas fa-water',
            'walking': 'fas fa-walking'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-compass')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            day_activities = []
            for i, activity in enumerate(base_activities):
                activity_copy = activity.copy()
                
                # Vary activities for different days
                if day > 1:
                    # Change some activities for variety
                    if i == 2:  # Third activity
                        if 'hiking' in activity_copy['type']:
                            activity_copy['title'] = 'Nature Walk Exploration'
                        elif 'boat' in activity_copy['type']:
                            activity_copy['title'] = 'River/Lake Exploration'
                
                day_activities.append(activity_copy)
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary

    def generate_relaxed_itinerary(self, trip, days):
        """Generate relaxed itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific relaxed activities
        activities_map = {
            'yangon': [
                {'time': '10:00 AM', 'title': 'Late Breakfast', 'location': 'Hotel Restaurant', 'duration': '1.5 hours', 'description': 'Leisurely morning meal', 'type': 'food'},
                {'time': '12:00 PM', 'title': 'Spa & Wellness', 'location': 'City Spa', 'duration': '2 hours', 'description': 'Relaxing massage and treatments', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Park Walk', 'location': 'Kandawgyi Park', 'duration': '1.5 hours', 'description': 'Gentle walk in beautiful park', 'type': 'walking'},
                {'time': '05:00 PM', 'title': 'Sunset Photography', 'location': 'Shwedagon Pagoda', 'duration': '1 hour', 'description': 'Capture beautiful sunset moments', 'type': 'photography'}
            ],
            'mandalay': [
                {'time': '10:00 AM', 'title': 'Royal Garden Visit', 'location': 'Mandalay Palace Gardens', 'duration': '2 hours', 'description': 'Leisurely walk in royal gardens', 'type': 'walking'},
                {'time': '01:00 PM', 'title': 'Traditional Spa', 'location': 'Local Wellness Center', 'duration': '2 hours', 'description': 'Traditional Myanmar spa treatments', 'type': 'wellness'},
                {'time': '04:00 PM', 'title': 'Tea House Relaxation', 'location': 'Local Tea House', 'duration': '1.5 hours', 'description': 'Relax with local tea culture', 'type': 'food'},
                {'time': '06:00 PM', 'title': 'Sunset River View', 'location': 'Irrawaddy Riverfront', 'duration': '1 hour', 'description': 'Peaceful sunset by the river', 'type': 'scenic'}
            ],
            'bagan': [
                {'time': '09:00 AM', 'title': 'Poolside Breakfast', 'location': 'Hotel Pool', 'duration': '1.5 hours', 'description': 'Relaxed breakfast with temple views', 'type': 'food'},
                {'time': '11:00 AM', 'title': 'Temple View Massage', 'location': 'Spa with View', 'duration': '2 hours', 'description': 'Massage with ancient temple views', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Leisurely E-Bike Ride', 'location': 'Quiet Temple Area', 'duration': '1.5 hours', 'description': 'Gentle e-bike ride to quiet temples', 'type': 'cycling'},
                {'time': '05:00 PM', 'title': 'Sunset Champagne', 'location': 'Sunset Viewpoint', 'duration': '1.5 hours', 'description': 'Champagne while watching sunset', 'type': 'scenic'}
            ],
            'inle lake': [
                {'time': '09:30 AM', 'title': 'Lakeside Breakfast', 'location': 'Lake View Restaurant', 'duration': '1.5 hours', 'description': 'Breakfast overlooking the lake', 'type': 'food'},
                {'time': '11:30 AM', 'title': 'Floating Spa Treatment', 'location': 'Lake Spa', 'duration': '2 hours', 'description': 'Spa treatments on the water', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Gentle Boat Ride', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'Leisurely boat tour of the lake', 'type': 'boat'},
                {'time': '05:30 PM', 'title': 'Lakeside Sunset', 'location': 'Lake Shore', 'duration': '1 hour', 'description': 'Peaceful sunset by the lake', 'type': 'scenic'}
            ]
        }
        
        base_activities = activities_map.get(destination_name, [
            {'time': '10:00 AM', 'title': 'Leisurely Breakfast', 'location': 'Hotel Restaurant', 'duration': '1.5 hours', 'description': 'Relaxed morning meal', 'type': 'food'},
            {'time': '12:00 PM', 'title': 'Wellness Session', 'location': 'Local Spa', 'duration': '2 hours', 'description': 'Relaxation and wellness treatments', 'type': 'wellness'},
            {'time': '03:00 PM', 'title': 'Gentle Exploration', 'location': 'Scenic Area', 'duration': '1.5 hours', 'description': f'Leisurely exploration of {trip.destination.name}', 'type': 'walking'},
            {'time': '05:00 PM', 'title': 'Sunset Viewing', 'location': 'Best View Spot', 'duration': '1 hour', 'description': 'Enjoy beautiful sunset views', 'type': 'scenic'}
        ])
        
        # Add icons
        icon_map = {
            'food': 'fas fa-utensils',
            'wellness': 'fas fa-spa',
            'walking': 'fas fa-walking',
            'photography': 'fas fa-camera',
            'scenic': 'fas fa-eye',
            'cycling': 'fas fa-bicycle',
            'boat': 'fas fa-ship'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-star')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': base_activities.copy()  # Same relaxed schedule each day
            })
        
        return itinerary

    def calculate_date(self, start_date, day_offset):
        """Calculate date for a specific day"""
        if start_date:
            return (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        return f"Day {day_offset + 1}"

class SelectPlanView(LoginRequiredMixin, View):
    """Handle plan selection"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, trip_id):
        try:
            trip = get_object_or_404(TripPlan, id=trip_id)
            
            # Check permissions
            if not request.user.is_staff and trip.user != request.user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'You do not have permission to select plans for this trip'
                    }, status=403)
                messages.error(request, 'You do not have permission to select plans for this trip')
                return redirect('planner:plan_selection', trip_id=trip_id)
            
            plan_id = request.POST.get('plan_id')
            
            if not plan_id:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'No plan selected'
                    }, status=400)
                messages.error(request, 'No plan selected')
                return redirect('planner:plan_selection', trip_id=trip_id)
            
            # Save to session
            request.session[f'selected_plan_{trip_id}'] = plan_id
            
            # Also save to trip object if it has the field
            if hasattr(trip, 'selected_plan'):
                try:
                    # Try to save as integer if possible
                    try:
                        plan_id_int = int(plan_id)
                        trip.selected_plan = plan_id_int
                    except ValueError:
                        trip.selected_plan = plan_id
                    
                    trip.save(update_fields=['selected_plan'])
                    print(f"Saved plan {plan_id} to trip {trip_id}")
                except Exception as e:
                    print(f"Error saving to trip: {e}")
            
            # Mark all other plans as not selected in session
            session_key = f'ai_plans_{trip_id}'
            plans = request.session.get(session_key, [])
            
            # Update the plan selection status in session
            for plan in plans:
                plan['is_selected'] = (str(plan.get('id')) == str(plan_id))
            
            # Save updated plans back to session
            request.session[session_key] = plans
            
            # Store selected plan details
            selected_plan = next((p for p in plans if str(p.get('id')) == str(plan_id)), None)
            if selected_plan:
                request.session[f'selected_plan_details_{trip_id}'] = selected_plan
            
            request.session.modified = True
            
            # If it's an AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Plan {plan_id} selected successfully!',
                    'selected_plan_id': plan_id,
                    'plan_title': selected_plan.get('title', '') if selected_plan else ''
                })
            
            # If regular form submission, redirect back
            messages.success(request, f'Plan selected successfully!')
            return redirect('planner:plan_selection', trip_id=trip_id)
            
        except Exception as e:
            print(f"Error in SelectPlanView: {e}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error selecting plan: {str(e)}'
                }, status=500)
            
            messages.error(request, f'Error selecting plan: {str(e)}')
            return redirect('planner:plan_selection', trip_id=trip_id)
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta

from .models import TripPlan
from .views import PlanSelectionView


class ItineraryDetailView(LoginRequiredMixin, View):
    """Display detailed itinerary with weather and activity management"""

    template_name = 'planner/itinerary_detail.html'

    def get(self, request, trip_id, plan_id):

        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)

        # Convert numeric plan_id to name
        plan_map = {
            '1': 'cultural',
            '2': 'adventure',
            '3': 'relaxed',
            1: 'cultural',
            2: 'adventure',
            3: 'relaxed',
        }

        if plan_id in plan_map:
            plan_id = plan_map.get(plan_id)

        elif isinstance(plan_id, str):
            plan_id = plan_id.lower().strip()

        # Generate itinerary
        days = trip.calculate_nights() + 1
        itinerary_generator = PlanSelectionView()

        if plan_id == 'cultural':
            days_data = itinerary_generator.generate_cultural_itinerary(trip, days)
            plan_title = 'Cultural Explorer'

        elif plan_id == 'adventure':
            days_data = itinerary_generator.generate_adventure_itinerary(trip, days)
            plan_title = 'Adventure Seeker'

        elif plan_id == 'relaxed':
            days_data = itinerary_generator.generate_relaxed_itinerary(trip, days)
            plan_title = 'Relaxed Wanderer'

        else:
            days_data = itinerary_generator.generate_cultural_itinerary(trip, days)
            plan_title = 'Cultural Explorer'
            plan_id = 'cultural'

        # Weather
        weather_forecast = self.get_weather_forecast_for_trip(trip)

        # Cost
        cost_estimate = self.calculate_cost_estimate(trip, plan_id)

        context = {
            'trip': trip,
            'plan_id': plan_id,
            'plan_title': plan_title,
            'days_data': days_data,
            'weather_forecast': weather_forecast,
            'cost_estimate': cost_estimate,
            'hotel': trip.selected_hotel,
            'transport': trip.selected_transport,
            'total_days': days,
            'total_activities': sum(len(day['activities']) for day in days_data) if days_data else 0,
            'destination_name': trip.destination.name,
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'travelers': trip.travelers,
            'nights': trip.calculate_nights(),
        }

        return render(request, self.template_name, context)

    # --------------------------------------------------
    # WEATHER
    # --------------------------------------------------

    def get_weather_forecast_for_trip(self, trip):

        try:
            from .weather_service import weather_service

            destination_name = trip.destination.name

            start_date = trip.start_date
            max_end_date = start_date + timedelta(days=4)
            actual_end_date = min(trip.end_date, max_end_date)

            forecast = weather_service.get_weather_forecast(
                destination_name,
                start_date.strftime('%Y-%m-%d'),
                actual_end_date.strftime('%Y-%m-%d')
            )

            if forecast:
                return dict(list(forecast.items())[:5])

            return self.generate_mock_weather_forecast(start_date, actual_end_date)

        except Exception:
            return self.generate_mock_weather_forecast(
                trip.start_date,
                trip.start_date + timedelta(days=4)
            )

    def generate_mock_weather_forecast(self, start_date, end_date):

        import random

        forecasts = {}
        current = start_date

        for _ in range(5):

            date_str = current.strftime('%Y-%m-%d')

            temp = random.randint(25, 35)

            forecasts[date_str] = {
                'date': date_str,
                'day_name': current.strftime('%A'),
                'daily_summary': {
                    'temperature': temp,
                    'description': 'Sunny',
                    'icon': '01d'
                },
                'min_temp': temp - 3,
                'max_temp': temp + 2,
                'is_mock': True,
            }

            current += timedelta(days=1)

        return forecasts

    # --------------------------------------------------
    # COST (FIXED)
    # --------------------------------------------------

    def calculate_cost_estimate(self, trip, plan_id):
        """
        Calculate cost estimate
        Includes: Hotel + Transport + Activities
        NO additional travelers
        """

        breakdown = trip.get_cost_breakdown()

        plan_multipliers = {
            'cultural': 1.0,
            'adventure': 1.15,
            'relaxed': 0.9,
       }

        multiplier = plan_multipliers.get(plan_id, 1.0)

    # Apply multiplier ONLY to destination
        destination_cost = int(
            breakdown.get('destination', 0) * multiplier
        )

        hotel_cost = int(breakdown.get('hotel', 0))
        transport_cost = int(breakdown.get('transport', 0))

    # ✅ FINAL TOTAL (WITH TRANSPORT)
        total = (
            hotel_cost +
            transport_cost +
            destination_cost
        )

        return {
            'total': total,
            'breakdown': {
                'hotel': hotel_cost,
                'transport': transport_cost,
                'destination': destination_cost,
            }
        }



class AddActivityView(LoginRequiredMixin, View):
    """Add a new activity to itinerary"""
    def post(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            day_number = data.get('day_number')
            activity_data = data.get('activity')
            
            return JsonResponse({
                'success': True,
                'message': 'Activity added successfully',
                'activity': activity_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class RemoveActivityView(LoginRequiredMixin, View):
    """Remove an activity from itinerary"""
    def post(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            day_number = data.get('day_number')
            activity_index = data.get('activity_index')
            
            return JsonResponse({
                'success': True,
                'message': 'Activity removed successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })





class TestWeatherAPIView(LoginRequiredMixin, View):
    """View to test weather API from browser"""
    def get(self, request):
        from .weather_service import weather_service
        import requests
        
        results = {
            'api_key_configured': bool(getattr(settings, 'OPENWEATHER_API_KEY', '')),
            'tests': []
        }
        
        # Test 1: Direct API call
        test_cases = [
            ("Yangon", "MM"),
            ("Mandalay", "MM"),
        ]
        
        for city, country in test_cases:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={weather_service.api_key}&units=metric"
            
            try:
                response = requests.get(url, timeout=5)
                data = response.json()
                
                if data.get('cod') == 200:
                    results['tests'].append({
                        'city': city,
                        'status': 'success',
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'message': 'API working'
                    })
                else:
                    results['tests'].append({
                        'city': city,
                        'status': 'api_error',
                        'message': data.get('message', 'Unknown API error')
                    })
                    
            except Exception as e:
                results['tests'].append({
                    'city': city,
                    'status': 'error',
                    'message': str(e)
                })
        
        # Test 2: Using weather service
        try:
            weather_data = weather_service.get_weather_by_city("Yangon")
            results['weather_service_test'] = {
                'status': 'success' if not weather_data.get('is_mock') else 'using_mock',
                'temperature': weather_data.get('temperature'),
                'is_mock': weather_data.get('is_mock', True),
                'message': 'Using real data' if not weather_data.get('is_mock') else 'Using mock data (API may be unavailable)'
            }
        except Exception as e:
            results['weather_service_test'] = {
                'status': 'error',
                'message': str(e)
            }
        
        return JsonResponse(results)
# ========== DESTINATION BROWSING VIEWS ==========
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from planner.models import Destination, Hotel



class RegionPlacesView(View):
    """Show all places/attractions in a region/city (ONLY attractions, not other cities)"""
    template_name = 'planner/region_places.html'
    
    def get(self, request, region_id):
        from .models import Destination, Hotel
        from .weather_service import WeatherService
        import re
        
        region = get_object_or_404(Destination, id=region_id, is_active=True)
        
        # IMPORTANT: Get ONLY places that have this region as parent AND are attractions
        places = Destination.objects.filter(
            parent=region,  # Must have this city as parent
            type='attraction',  # Must be attraction type
            is_active=True
        ).order_by('name')
        
        # Also include activities if they exist
        activities = Destination.objects.filter(
            parent=region,
            type='activity',
            is_active=True
        ).order_by('name')
        
        # Combine both
        all_places = list(places) + list(activities)
        
        # Debug print
        print(f"\n🔍 REGION PLACES PAGE - {region.name}:")
        for p in all_places:
            print(f"  - {p.name} (Type: {p.type})")
        print(f"  Total: {len(all_places)}\n")
        
        # Apply type filter if specified
        type_filter = request.GET.get('type')
        if type_filter and type_filter != 'all':
            if type_filter == 'attraction':
                all_places = [p for p in all_places if p.type == 'attraction']
            elif type_filter == 'activity':
                all_places = [p for p in all_places if p.type == 'activity']
        
        # Parse extra data from description for each place
        places_data = []
        for place in all_places:
            # Extract rating, reviews, features from description
            rating = None
            review_count = None
            entry_fee = "Free entry"
            distance = None
            features = []
            
            if place.description:
                # Try to extract rating
                rating_match = re.search(r'Rating:\s*([\d.]+)/5', place.description)
                if rating_match:
                    rating = float(rating_match.group(1))
                
                # Extract review count
                reviews_match = re.search(r'Reviews:\s*(\d+)', place.description)
                if reviews_match:
                    review_count = int(reviews_match.group(1))
                
                # Extract entry fee
                fee_match = re.search(r'Entry Fee:\s*(.+?)(?:\n|$)', place.description)
                if fee_match:
                    entry_fee = fee_match.group(1).strip()
                
                # Extract distance
                distance_match = re.search(r'Distance:\s*(.+?)(?:\n|$)', place.description)
                if distance_match:
                    distance = distance_match.group(1).strip()
                
                # Extract features
                features_match = re.search(r'Features:\s*(.+?)(?:\n|$)', place.description)
                if features_match:
                    features = [f.strip() for f in features_match.group(1).split(',')]
            
            places_data.append({
                'id': place.id,
                'name': place.name,
                'type': place.get_type_display(),
                'type_code': place.type,
                'description': place.description.split('\n\n')[0] if place.description else '',
                'rating': rating,
                'review_count': review_count,
                'entry_fee': entry_fee,
                'distance': distance,
                'features': features,
                'image': place.image,
                'has_image': bool(place.image),
                'region_name': region.name,
                'is_active': place.is_active
            })
        
        # Get hotels in this region
        hotels = Hotel.objects.filter(
            destination=region,
            is_active=True
        ).order_by('price_per_night')[:5]
        
        # Get weather for the region
        weather_service = WeatherService()
        if region.latitude and region.longitude:
            weather_data = weather_service.get_weather_by_coords(
                region.latitude,
                region.longitude,
                region.name
            )
        else:
            weather_data = weather_service.get_weather_by_city(region.name)
        
        context = {
            'region': region,
            'places': places_data,
            'places_count': len(places_data),
            'hotels': hotels,
            'weather_data': weather_data,
            'type_filter': type_filter,
            'all_types': ['attraction', 'activity'],
        }
        
        return render(request, self.template_name, context)
class PlaceDetailView(View):
    """Show detailed information about a specific place/attraction"""
    template_name = 'planner/place_detail.html'
    
    def get(self, request, place_id):
        from .models import Destination, Hotel
        from .weather_service import weather_service
        
        place = get_object_or_404(Destination, id=place_id, is_active=True)
        
        # Get weather
        if place.latitude and place.longitude:
            weather_data = weather_service.get_weather_by_coords(
                place.latitude,
                place.longitude,
                place.name
            )
        else:
            weather_data = weather_service.get_weather_by_city(place.name)
        
        # Get hotels in this area (if place has parent, use parent, otherwise use place itself)
        location = place.parent if place.parent else place
        hotels = Hotel.objects.filter(
            destination=location,
            is_active=True
        ).order_by('price_per_night')[:3]
        
        # Get similar places in the same region
        if place.parent:
            similar_places = Destination.objects.filter(
                parent=place.parent,
                is_active=True
            ).exclude(id=place.id)[:4]
        else:
            similar_places = Destination.objects.filter(
                region=place.region,
                is_active=True
            ).exclude(id=place.id)[:4]
        
        context = {
            'place': place,
            'weather_data': weather_data,
            'hotels': hotels,
            'similar_places': similar_places,
        }
        
        return render(request, self.template_name, context)
class DestinationDetailView(View):
    """Detailed view of a destination"""
    template_name = 'planner/destination_detail.html'

    def get(self, request, destination_id):
        destination = get_object_or_404(
            Destination,
            id=destination_id,
            is_active=True
        )

        from .weather_service import weather_service

        # Weather (coordinates first – fallback safe)
        if destination.latitude and destination.longitude:
            weather_data = weather_service.get_weather_by_coords(
                destination.latitude,
                destination.longitude,
                destination.name
            )
        else:
            weather_data = weather_service.get_weather_by_city(destination.name)

        # Hotels in this destination
        hotels = (
            Hotel.objects
            .filter(destination=destination, is_active=True)
            .order_by('price_per_night')[:5]
        )

        # Similar destinations
        similar_destinations = (
            Destination.objects
            .filter(region=destination.region, is_active=True)
            .exclude(id=destination.id)
            .order_by('?')[:4]
        )

        context = {
            'destination': destination,
            'weather_data': weather_data,
            'hotels': hotels,
            'similar_destinations': similar_destinations,
            'has_coordinates': bool(destination.latitude and destination.longitude),
        }

        return render(request, self.template_name, context)
class DestinationAutocompleteView(View):
    """AJAX endpoint for destination autocomplete - ONLY CITIES AND TOWNS"""
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        destinations = Destination.objects.filter(
            Q(name__icontains=query) | 
            Q(region__icontains=query),
            type__in=['city', 'town'],  # ← ADD THIS LINE
            is_active=True
        ).order_by('name')[:10]
        
        results = []
        for dest in destinations:
            results.append({
                'id': dest.id,
                'name': dest.name,
                'region': dest.region,
                'type': dest.get_type_display(),
                'full_name': f"{dest.name}, {dest.region}",
                'image_url': dest.image.url if dest.image else '',
            })
        
        return JsonResponse({'results': results})
class TripListView(LoginRequiredMixin, TemplateView):
    """View for showing all trips when clicking 'Total Trips' card"""
    template_name = 'planner/trip_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all trips for this user
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Categorize trips
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        )
        
        completed_trips = trips.filter(status='completed')
        
        # Prepare trip data for template
        trip_data = []
        for trip in trips:
            trip_data.append({
                'id': trip.id,
                'origin': trip.origin.name if trip.origin else 'Not specified',
                'destination': trip.destination.name if trip.destination else 'Not specified',
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,
                'status_display': trip.get_status_display(),
                'total_cost_mmk': trip.get_total_cost_in_mmk(),
                'travelers': trip.travelers,
                'created_at': trip.created_at,
                'is_upcoming': trip.start_date >= timezone.now().date() if trip.start_date else False,
                'is_completed': trip.status == 'completed',
                'has_hotel': bool(trip.selected_hotel),
                'has_transport': bool(trip.selected_transport),
            })
        
        context.update({
            'trips': trip_data,
            'total_trips': trips.count(),
            'upcoming_count': upcoming_trips.count(),
            'completed_count': completed_trips.count(),
            'total_spent_mmk': sum(trip.get_total_cost_in_mmk() for trip in trips.filter(status__in=['booked', 'completed'])),
        })
        
        return context


class UpcomingTripsView(LoginRequiredMixin, TemplateView):
    """View for showing only upcoming trips"""
    template_name = 'planner/upcoming_trips.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get upcoming trips (draft, planning, booked AND start_date in future)
        upcoming_trips = TripPlan.objects.filter(
            user=user,
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        ).order_by('start_date')
        
        # Prepare trip data
        trip_data = []
        for trip in upcoming_trips:
            trip_data.append({
                'id': trip.id,
                'origin': trip.origin.name if trip.origin else 'Not specified',
                'destination': trip.destination.name if trip.destination else 'Not specified',
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,
                'status_display': trip.get_status_display(),
                'total_cost_mmk': trip.get_total_cost_in_mmk(),
                'travelers': trip.travelers,
                'days_until': (trip.start_date - timezone.now().date()).days if trip.start_date else None,
                'hotel': trip.selected_hotel.name if trip.selected_hotel else 'Not selected',
                'transport': trip.selected_transport.get('name', 'Not selected') if trip.selected_transport else 'Not selected',
            })
        
        context.update({
            'upcoming_trips': trip_data,
            'total_upcoming': upcoming_trips.count(),
            'total_cost_mmk': sum(trip.get_total_cost_in_mmk() for trip in upcoming_trips),
        })
        
        return context


from django.views.generic import TemplateView


class TripCostAnalysisView(LoginRequiredMixin, TemplateView):
    """View for showing detailed cost analysis"""

    template_name = 'planner/trip_cost_analysis.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.request.user

        trips = TripPlan.objects.filter(user=user).order_by('-created_at')

        cost_breakdowns = []

        total_spent = 0
        total_estimated = 0

        for trip in trips:

            breakdown = trip.get_cost_breakdown()

            total = (
                breakdown.get('hotel', 0) +
                breakdown.get('transport', 0) +
                breakdown.get('destination', 0)
            )

            cost_data = {
                'trip': trip,
                'destination': trip.destination.name if trip.destination else 'Unknown',
                'dates': f"{trip.start_date.strftime('%b %d')} - {trip.end_date.strftime('%b %d, %Y')}",
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,

                'total_cost': total,

                'hotel_cost': breakdown.get('hotel', 0),
                'transport_cost': breakdown.get('transport', 0),
                'destination_cost': breakdown.get('destination', 0),
            }

            cost_breakdowns.append(cost_data)

            if trip.status in ['booked', 'completed']:
                total_spent += total

            total_estimated += total

        # Category totals
        hotel_total = sum(item['hotel_cost'] for item in cost_breakdowns)
        transport_total = sum(item['transport_cost'] for item in cost_breakdowns)
        destination_total = sum(item['destination_cost'] for item in cost_breakdowns)

        context.update({

            'cost_breakdowns': cost_breakdowns,

            'total_spent_mmk': total_spent,
            'total_estimated_mmk': total_estimated,

            'hotel_total_mmk': hotel_total,
            'transport_total_mmk': transport_total,
            'destination_total_mmk': destination_total,

            'total_trips': trips.count(),
            'booked_completed_trips': trips.filter(
                status__in=['booked', 'completed']
            ).count(),
        })

        return context



class VisitedDestinationsView(LoginRequiredMixin, TemplateView):
    """View for showing visited destinations when clicking 'Destinations Visited' card"""
    template_name = 'planner/visited_destinations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get TODAY'S DATE (dynamic, not hardcoded)
        today = timezone.now().date()
        
        # Get trips that have been completed (status='completed') OR have ended (end_date < today)
        visited_trips = TripPlan.objects.filter(
            user=user
        ).filter(
            Q(status='completed') | Q(end_date__lt=today)
        ).exclude(
            status='cancelled'
        ).order_by('-end_date')
        
        print(f"DEBUG: Today's date: {today}")
        print(f"DEBUG: Found {visited_trips.count()} visited trips")
        
        # Group destinations by visit date
        visited_destinations_by_month = {}
        destination_stats = {}
        
        for trip in visited_trips:
            if trip.destination:
                dest_name = trip.destination.name
                dest_region = trip.destination.region
                visit_date = trip.end_date  # Last day of the trip
                
                print(f"DEBUG: {dest_name} - End: {visit_date}, Status: {trip.status}")
                
                # Group by year-month for timeline
                year_month = visit_date.strftime('%Y-%m')
                if year_month not in visited_destinations_by_month:
                    visited_destinations_by_month[year_month] = []
                
                visited_destinations_by_month[year_month].append({
                    'destination': trip.destination,
                    'visit_date': visit_date,
                    'trip': trip,
                    'duration_days': trip.calculate_nights() + 1,
                    'travelers': trip.travelers,
                    'total_cost_mmk': trip.get_total_cost_in_mmk(),
                    'status': trip.status,
                })
                
                # Initialize destination stats if first time
                if dest_name not in destination_stats:
                    destination_stats[dest_name] = {
                        'destination': trip.destination,
                        'destination_region': dest_region,
                        'visit_count': 0,
                        'last_visit': visit_date,  # Will be updated if newer
                        'total_days': 0,
                        'total_spent': 0,
                        'trips': []
                    }
                else:
                    # Update last_visit if this trip is more recent
                    if visit_date > destination_stats[dest_name]['last_visit']:
                        destination_stats[dest_name]['last_visit'] = visit_date
                
                # Update stats
                destination_stats[dest_name]['visit_count'] += 1
                destination_stats[dest_name]['total_days'] += (trip.calculate_nights() + 1)
                destination_stats[dest_name]['total_spent'] += trip.get_total_cost_in_mmk()
                destination_stats[dest_name]['trips'].append({
                    'date': visit_date,
                    'duration': trip.calculate_nights() + 1,
                    'cost': trip.get_total_cost_in_mmk(),
                    'status': trip.status
                })
        
        # Calculate average cost per day for each destination
        for dest_name, stats in destination_stats.items():
            if stats['total_days'] > 0:
                stats['avg_cost_per_day'] = int(stats['total_spent'] / stats['total_days'])
            else:
                stats['avg_cost_per_day'] = 0
        
        # Sort destinations by last visit date (most recent first)
        sorted_destinations = sorted(
            destination_stats.values(),
            key=lambda x: x['last_visit'],
            reverse=True
        )
        
        # Sort visited destinations by month (most recent first)
        sorted_visited_months = sorted(
            visited_destinations_by_month.items(),
            key=lambda x: x[0],
            reverse=True
        )
        
        context.update({
            'visited_destinations': dict(sorted_visited_months),
            'destination_stats': sorted_destinations,
            'total_destinations_visited': len(destination_stats),
            'total_visited_trips': visited_trips.count(),
            'total_days_traveled': sum(trip.calculate_nights() + 1 for trip in visited_trips),
            'total_spent_mmk': sum(trip.get_total_cost_in_mmk() for trip in visited_trips),
            'today': today,
        })
        
        return context
# ========== CONFIRM BOOKING VIEW ==========
# ========== CONFIRM BOOKING VIEW ==========
# ========== CONFIRM BOOKING VIEW ==========
# ========== CONFIRM BOOKING VIEW ==========
class ConfirmBookingView(LoginRequiredMixin, View):

    def post(self, request, trip_id):

        trip = get_object_or_404(
            TripPlan,
            id=trip_id,
            user=request.user
        )

        if not trip.selected_plan:
            messages.error(request, "Select plan first")
            return redirect('planner:plan_selection', trip_id=trip.id)

        if not trip.selected_hotel:
            messages.error(request, "Select hotel")
            return redirect('planner:plan_selection', trip_id=trip.id)

        if not trip.selected_transport:
            messages.error(request, "Select transport")
            return redirect('planner:plan_selection', trip_id=trip.id)


        transport = trip.selected_transport

        # AUTO CONFIRM
        if transport.get("is_temporary"):

            success = self.auto_confirm(trip, request)

            if not success:
                messages.error(request, "Seat confirmation failed")
                return redirect('planner:plan_selection', trip_id=trip.id)


        trip.is_confirmed = True
        trip.confirmed_at = timezone.now()
        trip.status = "booked"

        trip.save()

        messages.success(request, "Trip booked successfully")

        return redirect(
            "planner:itinerary_detail",
            trip_id=trip.id,
            plan_id="cultural"
        )


    def auto_confirm(self, trip, request):

        try:

            data = trip.selected_transport

            t_type = data["type"]
            t_id = data["id"]
            seats = data["seats"]
            date = trip.start_date

            schedule = get_object_or_404(
                TransportSchedule,
                transport_type=t_type,
                transport_id=t_id,
                travel_date=date,
                is_active=True
            )

            for seat in seats:

                if BookedSeat.objects.filter(
                    transport_type=t_type,
                    transport_id=t_id,
                    schedule_date=date,
                    seat_number=seat,
                    is_cancelled=False
                ).exists():
                    return False


                BookedSeat.objects.create(
                    transport_type=t_type,
                    transport_id=t_id,
                    schedule_date=date,
                    seat_number=seat,
                    trip=trip,
                    booked_by=request.user
                )

            schedule.available_seats -= len(seats)
            schedule.save()

            trip.selected_transport["is_temporary"] = False
            trip.selected_transport["needs_confirmation"] = False

            trip.save()

            return True

        except Exception as e:
            print("AUTO CONFIRM ERROR:", e)
            return False
def how_it_works(request):
     """Render the How It Works page"""
     return render(request, 'how_it_works.html')
# ========== ROOM SELECTION VIEWS ==========

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Add these imports at the top




class GetAvailableRoomsView(LoginRequiredMixin, View):
    """AJAX endpoint to get available rooms"""
    
    def get(self, request, hotel_id):
        hotel = get_object_or_404(Hotel, id=hotel_id)
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = int(request.GET.get('guests', 1))
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid dates'})
        
        available_rooms = hotel.get_available_rooms(check_in_date, check_out_date, guests)
        
        rooms_data = []
        for room in available_rooms:
            rooms_data.append({
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type.name,
                'max_occupancy': room.room_type.max_occupancy,
                'price_per_night': float(room.get_price_per_night()),
                'has_window': room.has_window,
                'has_balcony': room.has_balcony,
                'floor': room.floor,
            })
        
        return JsonResponse({
            'success': True,
            'rooms': rooms_data,
            'count': len(rooms_data)
        })


# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Add these imports at the top


class SelectRoomsView(LoginRequiredMixin, View):
    """View for selecting rooms in a hotel"""
    template_name = 'planner/select_rooms.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        if not trip.selected_hotel:
            messages.error(request, 'Please select a hotel first')
            return redirect('planner:select_hotel_map', trip_id=trip.id)
        
        hotel = trip.selected_hotel
        check_in = trip.start_date
        check_out = trip.end_date
        guests = trip.travelers
        nights = trip.calculate_nights()
        
        # Get available rooms for these dates
        available_rooms = self.get_available_rooms(hotel, check_in, check_out, guests)
        
        # Group rooms by type
        rooms_by_type = {}
        for room in available_rooms:
            room_type = room.room_type
            if room_type.id not in rooms_by_type:
                rooms_by_type[room_type.id] = {
                    'room_type': room_type,
                    'rooms': [],
                    'price_per_night': room.get_price_per_night()
                }
            rooms_by_type[room_type.id]['rooms'].append(room)
        
        context = {
            'trip': trip,
            'hotel': hotel,
            'rooms_by_type': rooms_by_type,
            'check_in': check_in,
            'check_out': check_out,
            'nights': nights,
            'guests': guests,
        }
        
        return render(request, self.template_name, context)
    
    def get_available_rooms(self, hotel, check_in, check_out, guests):
        """Get all available rooms for given dates"""
        from django.db.models import Exists, OuterRef
        
        # Get all active rooms in this hotel that can accommodate guests
        all_rooms = Room.objects.filter(
            hotel=hotel, 
            is_active=True,
            room_type__max_occupancy__gte=guests
        )
        
        date_range = [check_in + timedelta(days=x) for x in range((check_out - check_in).days)]
        
        # Filter out rooms with any booking or unavailable dates
        available_rooms = []
        for room in all_rooms:
            is_available = True
            
            # Check for bookings
            if RoomBooking.objects.filter(
                room=room,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
                is_cancelled=False,
                status__in=['temporary', 'confirmed', 'checked_in']
            ).exists():
                is_available = False
            
            # Check availability records
            if is_available:
                unavailable_dates = RoomAvailability.objects.filter(
                    room=room,
                    date__in=date_range,
                    is_available=False
                ).exists()
                if unavailable_dates:
                    is_available = False
            
            if is_available:
                available_rooms.append(room)
        
        return available_rooms

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

class SaveRoomSelectionView(LoginRequiredMixin, View):
    """Save room selection and redirect back to plan page"""
    
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            room_ids = data.get('room_ids', [])
            
            if not room_ids:
                return JsonResponse({'success': False, 'error': 'No rooms selected'})
            
            # Validate availability again
            hotel = trip.selected_hotel
            if not hotel:
                return JsonResponse({'success': False, 'error': 'No hotel selected'})
            
            check_in = trip.start_date
            check_out = trip.end_date
            nights = trip.calculate_nights()
            
            # Check room availability
            from .models_room import Room, RoomBooking, RoomAvailability
            date_range = [check_in + timedelta(days=x) for x in range((check_out - check_in).days)]
            
            invalid_rooms = []
            for room_id in room_ids:
                room = Room.objects.get(id=room_id)
                
                # Check for bookings
                has_booking = RoomBooking.objects.filter(
                    room=room,
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in,
                    is_cancelled=False,
                    status__in=['temporary', 'confirmed', 'checked_in']
                ).exists()
                
                # Check availability records
                has_unavailable = RoomAvailability.objects.filter(
                    room=room,
                    date__in=date_range,
                    is_available=False
                ).exists()
                
                if has_booking or has_unavailable:
                    invalid_rooms.append(room_id)
            
            if invalid_rooms:
                return JsonResponse({
                    'success': False, 
                    'error': 'Some rooms are no longer available',
                    'invalid_rooms': invalid_rooms
                })
            
            # Calculate price based on room prices ONLY
            rooms = Room.objects.filter(id__in=room_ids)
            total_price = 0
            room_details = []
            
            for room in rooms:
                price_per_night = room.get_price_per_night()
                # CORRECT calculation - price_per_night × nights
                room_total = price_per_night * nights
                total_price += room_total
                room_details.append({
                    'id': room.id,
                    'room_number': room.room_number,
                    'room_type': room.room_type.name,
                    'price_per_night': float(price_per_night),
                    'total': float(room_total),  # This is now correct
                    'floor': room.floor,
                    'bed_type': room.bed_type
                })
            
            # Save to trip
            trip.selected_rooms = {
                'room_ids': room_ids,
                'total_price': float(total_price),  # Store the correct total
                'room_details': room_details,
                'is_temporary': True
            }
            trip.save()
            
            print(f"DEBUG - Saved rooms: {room_details}")
            print(f"DEBUG - Total price: {total_price} for {nights} nights")
            
            # Build redirect URL to MAIN PLAN PAGE
            redirect_url = reverse('planner:plan')
            params = []
            
            # Include origin and destination
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={urllib.parse.quote(trip.origin.name)}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={urllib.parse.quote(trip.destination.name)}')
            
            # Add hotel
            if trip.selected_hotel:
                params.append(f'hotel_id={trip.selected_hotel.id}')
                params.append(f'hotel_name={urllib.parse.quote(trip.selected_hotel.name)}')
            
            # Add dates
            if trip.start_date:
                params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
            if trip.end_date:
                params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
            
            # Add travelers
            params.append(f'travelers={trip.travelers}')
            
            # Check if transport exists and include it
            if trip.selected_transport:
                transport_data = trip.selected_transport
                if transport_data.get('id'):
                    params.append(f'transport_id={transport_data.get("id")}')
                    params.append(f'transport_type={transport_data.get("type", "")}')
                    params.append(f'transport_name={urllib.parse.quote(transport_data.get("name", ""))}')
            
            # Build final URL
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return JsonResponse({
                'success': True,
                'message': f'{len(room_ids)} room(s) selected',
                'total_price': float(total_price),
                'room_details': room_details,
                'redirect_url': redirect_url
            })
            
        except Exception as e:
            print(f"Error in SaveRoomSelectionView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})

class ConfirmRoomBookingView(LoginRequiredMixin, View):
    """Confirm room booking (create actual RoomBooking records)"""
    
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        if not hasattr(trip, 'selected_rooms') or not trip.selected_rooms:
            messages.error(request, 'No rooms selected to confirm')
            return redirect('planner:plan_selection', trip_id=trip.id)
        
        room_data = trip.selected_rooms
        room_ids = room_data.get('room_ids', [])
        
        if not room_ids:
            messages.error(request, 'No rooms to book')
            return redirect('planner:plan_selection', trip_id=trip.id)
        
        # Double-check availability before confirming
        hotel = trip.selected_hotel
        check_in = trip.start_date
        check_out = trip.end_date
        
        for room_id in room_ids:
            if not hotel.check_room_availability(room_id, check_in, check_out):
                messages.error(request, f'Room {room_id} is no longer available')
                return redirect('planner:select_rooms', trip_id=trip.id)
        
        # Create bookings
        nights = trip.calculate_nights()
        bookings_created = []
        
        for room_id in room_ids:
            room = Room.objects.get(id=room_id)
            price_per_night = room.get_price_per_night()
            total_price = price_per_night * nights
            
            booking = RoomBooking.objects.create(
                room=room,
                trip=trip,
                booked_by=request.user,
                check_in_date=check_in,
                check_out_date=check_out,
                guests=trip.travelers,
                price_per_night=price_per_night,
                total_price=total_price,
                status='confirmed'
            )
            bookings_created.append(booking)
        
        # Update trip status
        trip.selected_rooms['is_temporary'] = False
        trip.selected_rooms['booking_ids'] = [b.id for b in bookings_created]
        trip.status = 'booked'
        trip.save()
        
        messages.success(request, f'{len(bookings_created)} room(s) booked successfully!')
        return redirect('planner:itinerary_detail', trip_id=trip.id, plan_id='cultural')