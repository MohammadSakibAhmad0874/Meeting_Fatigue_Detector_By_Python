import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import datetime
from datetime import timedelta
import random
import re
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class MeetingFatigueDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Fatigue Detector")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.meetings = []
        self.emails = []
        self.work_patterns = {}
        self.fatigue_score = 0
        self.break_suggestions = []
        
        # Initialize sentiment analysis keywords
        self.positive_words = ['great', 'excellent', 'good', 'happy', 'satisfied', 'pleased', 'wonderful', 'amazing', 'fantastic']
        self.negative_words = ['tired', 'exhausted', 'stressed', 'overwhelmed', 'frustrated', 'difficult', 'problem', 'issue', 'concern', 'busy']
        self.fatigue_words = ['fatigue', 'burnout', 'overworked', 'drained', 'exhaustion', 'overwhelm']
        
        self.setup_ui()
        self.generate_sample_data()
        
    def setup_ui(self):
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.setup_dashboard_tab(notebook)
        
        # Data Input tab
        self.setup_data_input_tab(notebook)
        
        # Analysis tab
        self.setup_analysis_tab(notebook)
        
        # Recommendations tab
        self.setup_recommendations_tab(notebook)
        
    def setup_dashboard_tab(self, notebook):
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Dashboard")
        
        # Title
        title_label = tk.Label(dashboard_frame, text="Meeting Fatigue Dashboard", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Metrics frame
        metrics_frame = tk.Frame(dashboard_frame, bg='#f0f0f0')
        metrics_frame.pack(fill='x', padx=20, pady=10)
        
        # Fatigue score display
        self.fatigue_label = tk.Label(metrics_frame, text="Fatigue Score: 0/100", 
                                     font=('Arial', 14, 'bold'), bg='#f0f0f0')
        self.fatigue_label.pack(side='left')
        
        # Status indicator
        self.status_label = tk.Label(metrics_frame, text="Status: Analyzing...", 
                                    font=('Arial', 12), bg='#f0f0f0')
        self.status_label.pack(side='right')
        
        # Progress bar for fatigue level
        self.fatigue_progress = ttk.Progressbar(dashboard_frame, length=400, mode='determinate')
        self.fatigue_progress.pack(pady=10)
        
        # Chart frame
        chart_frame = tk.Frame(dashboard_frame, bg='#f0f0f0')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create matplotlib figure for charts
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Update button
        update_btn = tk.Button(dashboard_frame, text="Update Analysis", 
                              command=self.update_analysis, bg='#4CAF50', fg='white',
                              font=('Arial', 12, 'bold'))
        update_btn.pack(pady=10)
        
    def setup_data_input_tab(self, notebook):
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="Data Input")
        
        # Meeting input section
        meeting_frame = tk.LabelFrame(input_frame, text="Add Meeting", font=('Arial', 12, 'bold'))
        meeting_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(meeting_frame, text="Meeting Title:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.meeting_title = tk.Entry(meeting_frame, width=30)
        self.meeting_title.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(meeting_frame, text="Duration (minutes):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.meeting_duration = tk.Entry(meeting_frame, width=30)
        self.meeting_duration.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(meeting_frame, text="Type:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.meeting_type = ttk.Combobox(meeting_frame, values=['Regular', 'Important', 'Urgent', 'Routine'], width=27)
        self.meeting_type.grid(row=2, column=1, padx=5, pady=5)
        
        add_meeting_btn = tk.Button(meeting_frame, text="Add Meeting", 
                                   command=self.add_meeting, bg='#2196F3', fg='white')
        add_meeting_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Email input section
        email_frame = tk.LabelFrame(input_frame, text="Add Email Data", font=('Arial', 12, 'bold'))
        email_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(email_frame, text="Email Content:").pack(anchor='w', padx=5, pady=5)
        self.email_text = scrolledtext.ScrolledText(email_frame, height=5, width=60)
        self.email_text.pack(padx=5, pady=5)
        
        add_email_btn = tk.Button(email_frame, text="Add Email", 
                                 command=self.add_email, bg='#FF9800', fg='white')
        add_email_btn.pack(pady=10)
        
        # Work pattern input
        pattern_frame = tk.LabelFrame(input_frame, text="Work Pattern", font=('Arial', 12, 'bold'))
        pattern_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(pattern_frame, text="Daily Work Hours:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.work_hours = tk.Entry(pattern_frame, width=30)
        self.work_hours.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(pattern_frame, text="Sleep Hours:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.sleep_hours = tk.Entry(pattern_frame, width=30)
        self.sleep_hours.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(pattern_frame, text="Stress Level (1-10):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.stress_level = tk.Scale(pattern_frame, from_=1, to=10, orient='horizontal')
        self.stress_level.grid(row=2, column=1, padx=5, pady=5)
        
        update_pattern_btn = tk.Button(pattern_frame, text="Update Pattern", 
                                      command=self.update_work_pattern, bg='#9C27B0', fg='white')
        update_pattern_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
    def setup_analysis_tab(self, notebook):
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        
        # Analysis results display
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=25, width=80)
        self.analysis_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Analyze button
        analyze_btn = tk.Button(analysis_frame, text="Run Full Analysis", 
                               command=self.run_analysis, bg='#FF5722', fg='white',
                               font=('Arial', 12, 'bold'))
        analyze_btn.pack(pady=10)
        
    def setup_recommendations_tab(self, notebook):
        rec_frame = ttk.Frame(notebook)
        notebook.add(rec_frame, text="Recommendations")
        
        # Recommendations display
        self.recommendations_text = scrolledtext.ScrolledText(rec_frame, height=20, width=80)
        self.recommendations_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Generate recommendations button
        gen_rec_btn = tk.Button(rec_frame, text="Generate Recommendations", 
                               command=self.generate_recommendations, bg='#4CAF50', fg='white',
                               font=('Arial', 12, 'bold'))
        gen_rec_btn.pack(pady=10)
        
        # Export recommendations button
        export_btn = tk.Button(rec_frame, text="Export Report", 
                              command=self.export_report, bg='#607D8B', fg='white')
        export_btn.pack(pady=5)
        
    def generate_sample_data(self):
        """Generate sample data for demonstration"""
        # Sample meetings
        meeting_types = ['Daily Standup', 'Project Review', 'Client Call', 'Team Sync', 'Strategy Meeting']
        for i in range(15):
            self.meetings.append({
                'title': f"{random.choice(meeting_types)} {i+1}",
                'duration': random.randint(30, 120),
                'type': random.choice(['Regular', 'Important', 'Urgent', 'Routine']),
                'date': datetime.datetime.now() - timedelta(days=random.randint(0, 7))
            })
        
        # Sample emails
        sample_emails = [
            "Feeling a bit overwhelmed with the current workload. Need to discuss priorities.",
            "Great progress on the project! Team is doing excellent work.",
            "Having trouble keeping up with all the meetings this week. Very tired.",
            "Excited about the new initiative. Looking forward to collaboration.",
            "Stressed about the upcoming deadline. Need more time to complete tasks."
        ]
        for email in sample_emails:
            self.emails.append({'content': email, 'date': datetime.datetime.now()})
        
        # Sample work pattern
        self.work_patterns = {
            'work_hours': 9,
            'sleep_hours': 7,
            'stress_level': 6
        }
        
    def add_meeting(self):
        title = self.meeting_title.get()
        try:
            duration = int(self.meeting_duration.get())
            meeting_type = self.meeting_type.get()
            
            if title and duration and meeting_type:
                self.meetings.append({
                    'title': title,
                    'duration': duration,
                    'type': meeting_type,
                    'date': datetime.datetime.now()
                })
                
                # Clear inputs
                self.meeting_title.delete(0, tk.END)
                self.meeting_duration.delete(0, tk.END)
                self.meeting_type.set('')
                
                messagebox.showinfo("Success", "Meeting added successfully!")
            else:
                messagebox.showwarning("Warning", "Please fill all fields!")
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number!")
    
    def add_email(self):
        content = self.email_text.get(1.0, tk.END).strip()
        if content:
            self.emails.append({
                'content': content,
                'date': datetime.datetime.now()
            })
            self.email_text.delete(1.0, tk.END)
            messagebox.showinfo("Success", "Email data added successfully!")
        else:
            messagebox.showwarning("Warning", "Please enter email content!")
    
    def update_work_pattern(self):
        try:
            work_hours = float(self.work_hours.get()) if self.work_hours.get() else 8
            sleep_hours = float(self.sleep_hours.get()) if self.sleep_hours.get() else 7
            stress_level = self.stress_level.get()
            
            self.work_patterns = {
                'work_hours': work_hours,
                'sleep_hours': sleep_hours,
                'stress_level': stress_level
            }
            messagebox.showinfo("Success", "Work pattern updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def analyze_meeting_load(self):
        """Analyze meeting load and patterns"""
        if not self.meetings:
            return 0, "No meetings to analyze"
        
        total_duration = sum(meeting['duration'] for meeting in self.meetings)
        avg_duration = total_duration / len(self.meetings)
        
        # Calculate fatigue based on meeting load
        daily_meetings = len([m for m in self.meetings if m['date'].date() == datetime.date.today()])
        weekly_duration = sum(m['duration'] for m in self.meetings 
                            if m['date'] >= datetime.datetime.now() - timedelta(days=7))
        
        # Fatigue scoring
        load_score = min((weekly_duration / 60) * 2, 40)  # Hours to score (max 40)
        frequency_score = min(daily_meetings * 5, 30)     # Daily meetings (max 30)
        
        analysis = f"Meeting Load Analysis:\n"
        analysis += f"- Total meetings: {len(self.meetings)}\n"
        analysis += f"- Average duration: {avg_duration:.1f} minutes\n"
        analysis += f"- Weekly meeting time: {weekly_duration/60:.1f} hours\n"
        analysis += f"- Today's meetings: {daily_meetings}\n"
        analysis += f"- Load fatigue score: {load_score:.1f}/40\n"
        
        return load_score + frequency_score, analysis
    
    def analyze_email_sentiment(self):
        """Analyze email sentiment for fatigue indicators"""
        if not self.emails:
            return 0, "No emails to analyze"
        
        sentiment_scores = []
        fatigue_indicators = 0
        
        for email in self.emails:
            content = email['content'].lower()
            
            # Count positive and negative words
            positive_count = sum(1 for word in self.positive_words if word in content)
            negative_count = sum(1 for word in self.negative_words if word in content)
            fatigue_count = sum(1 for word in self.fatigue_words if word in content)
            
            # Calculate sentiment score
            sentiment = positive_count - negative_count - (fatigue_count * 2)
            sentiment_scores.append(sentiment)
            
            if fatigue_count > 0 or negative_count > positive_count:
                fatigue_indicators += 1
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        fatigue_ratio = fatigue_indicators / len(self.emails)
        
        # Convert to fatigue score (0-30)
        sentiment_fatigue = max(0, 15 - avg_sentiment * 3)
        ratio_fatigue = fatigue_ratio * 15
        
        analysis = f"Email Sentiment Analysis:\n"
        analysis += f"- Total emails analyzed: {len(self.emails)}\n"
        analysis += f"- Average sentiment: {avg_sentiment:.2f}\n"
        analysis += f"- Fatigue indicators: {fatigue_indicators}\n"
        analysis += f"- Fatigue ratio: {fatigue_ratio:.2%}\n"
        analysis += f"- Sentiment fatigue score: {sentiment_fatigue + ratio_fatigue:.1f}/30\n"
        
        return sentiment_fatigue + ratio_fatigue, analysis
    
    def analyze_work_patterns(self):
        """Analyze work patterns for fatigue risk"""
        if not self.work_patterns:
            return 0, "No work pattern data available"
        
        work_hours = self.work_patterns.get('work_hours', 8)
        sleep_hours = self.work_patterns.get('sleep_hours', 7)
        stress_level = self.work_patterns.get('stress_level', 5)
        
        # Calculate fatigue based on work patterns
        work_fatigue = max(0, (work_hours - 8) * 3)  # Excess work hours
        sleep_fatigue = max(0, (7 - sleep_hours) * 4)  # Sleep deficit
        stress_fatigue = stress_level * 2  # Stress contribution
        
        total_pattern_fatigue = min(work_fatigue + sleep_fatigue + stress_fatigue, 30)
        
        analysis = f"Work Pattern Analysis:\n"
        analysis += f"- Daily work hours: {work_hours}\n"
        analysis += f"- Sleep hours: {sleep_hours}\n"
        analysis += f"- Stress level: {stress_level}/10\n"
        analysis += f"- Work hour fatigue: {work_fatigue:.1f}\n"
        analysis += f"- Sleep deficit fatigue: {sleep_fatigue:.1f}\n"
        analysis += f"- Stress fatigue: {stress_fatigue:.1f}\n"
        analysis += f"- Total pattern fatigue: {total_pattern_fatigue:.1f}/30\n"
        
        return total_pattern_fatigue, analysis
    
    def calculate_overall_fatigue(self):
        """Calculate overall fatigue score"""
        meeting_score, meeting_analysis = self.analyze_meeting_load()
        sentiment_score, sentiment_analysis = self.analyze_email_sentiment()
        pattern_score, pattern_analysis = self.analyze_work_patterns()
        
        self.fatigue_score = min(meeting_score + sentiment_score + pattern_score, 100)
        
        return self.fatigue_score, meeting_analysis, sentiment_analysis, pattern_analysis
    
    def get_fatigue_status(self, score):
        """Get fatigue status based on score"""
        if score < 30:
            return "Low Fatigue", "green"
        elif score < 60:
            return "Moderate Fatigue", "orange"
        else:
            return "High Fatigue", "red"
    
    def update_analysis(self):
        """Update the dashboard with current analysis"""
        score, meeting_analysis, sentiment_analysis, pattern_analysis = self.calculate_overall_fatigue()
        status, color = self.get_fatigue_status(score)
        
        # Update labels
        self.fatigue_label.config(text=f"Fatigue Score: {score:.1f}/100")
        self.status_label.config(text=f"Status: {status}", fg=color)
        
        # Update progress bar
        self.fatigue_progress['value'] = score
        
        # Update charts
        self.update_charts()
        
        messagebox.showinfo("Analysis Updated", f"Current fatigue score: {score:.1f}\nStatus: {status}")
    
    def update_charts(self):
        """Update the dashboard charts"""
        self.ax1.clear()
        self.ax2.clear()
        
        # Chart 1: Meeting duration distribution
        if self.meetings:
            durations = [m['duration'] for m in self.meetings]
            self.ax1.hist(durations, bins=10, alpha=0.7, color='skyblue')
            self.ax1.set_title('Meeting Duration Distribution')
            self.ax1.set_xlabel('Duration (minutes)')
            self.ax1.set_ylabel('Frequency')
        
        # Chart 2: Fatigue components
        components = ['Meetings', 'Sentiment', 'Work Pattern']
        meeting_score, _ = self.analyze_meeting_load()
        sentiment_score, _ = self.analyze_email_sentiment()
        pattern_score, _ = self.analyze_work_patterns()
        
        scores = [meeting_score, sentiment_score, pattern_score]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        self.ax2.bar(components, scores, color=colors, alpha=0.7)
        self.ax2.set_title('Fatigue Score Components')
        self.ax2.set_ylabel('Score')
        
        self.canvas.draw()
    
    def run_analysis(self):
        """Run comprehensive analysis and display results"""
        score, meeting_analysis, sentiment_analysis, pattern_analysis = self.calculate_overall_fatigue()
        status, _ = self.get_fatigue_status(score)
        
        # Clear previous analysis
        self.analysis_text.delete(1.0, tk.END)
        
        # Display comprehensive analysis
        analysis_report = f"""COMPREHENSIVE FATIGUE ANALYSIS REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
OVERALL FATIGUE SCORE: {score:.1f}/100
STATUS: {status}
{'='*60}

{meeting_analysis}

{'='*60}
{sentiment_analysis}

{'='*60}
{pattern_analysis}

{'='*60}
RISK ASSESSMENT:
"""
        
        # Add risk assessment
        if score < 30:
            analysis_report += "✅ LOW RISK: You're managing your workload well. Continue current practices.\n"
        elif score < 60:
            analysis_report += "⚠️ MODERATE RISK: Consider taking breaks and optimizing your schedule.\n"
        else:
            analysis_report += "🚨 HIGH RISK: Immediate action needed to prevent burnout.\n"
        
        # Add specific recommendations based on highest contributing factor
        meeting_score, _ = self.analyze_meeting_load()
        sentiment_score, _ = self.analyze_email_sentiment()
        pattern_score, _ = self.analyze_work_patterns()
        
        max_score = max(meeting_score, sentiment_score, pattern_score)
        
        if max_score == meeting_score:
            analysis_report += "\nPRIMARY CONCERN: Meeting overload\n"
        elif max_score == sentiment_score:
            analysis_report += "\nPRIMARY CONCERN: Negative sentiment indicators\n"
        else:
            analysis_report += "\nPRIMARY CONCERN: Work-life balance issues\n"
        
        self.analysis_text.insert(tk.END, analysis_report)
    
    def generate_recommendations(self):
        """Generate personalized recommendations"""
        score, _, _, _ = self.calculate_overall_fatigue()
        meeting_score, _ = self.analyze_meeting_load()
        sentiment_score, _ = self.analyze_email_sentiment()
        pattern_score, _ = self.analyze_work_patterns()
        
        # Clear previous recommendations
        self.recommendations_text.delete(1.0, tk.END)
        
        recommendations = f"""PERSONALIZED RECOMMENDATIONS
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Based on your fatigue score of {score:.1f}/100, here are tailored recommendations:

"""
        
        # Meeting-related recommendations
        if meeting_score > 20:
            recommendations += """🗓️ MEETING OPTIMIZATION:
• Implement "No Meeting Fridays" or dedicate specific days for focused work
• Use the 25-minute rule: limit routine meetings to 25 minutes instead of 30
• Schedule buffer time (15 minutes) between meetings
• Batch similar meetings together to maintain focus
• Consider converting some meetings to async updates via email/Slack
• Decline non-essential meetings that don't require your direct input

"""
        
        # Sentiment-based recommendations
        if sentiment_score > 10:
            recommendations += """😌 MENTAL WELLNESS:
• Practice the 2-minute rule: take 2 minutes between tasks to breathe deeply
• Use positive affirmations in your daily routine
• Schedule regular check-ins with your manager about workload
• Consider using a mood tracking app to identify patterns
• Implement a "gratitude practice" - write down 3 positive things daily
• Take walking breaks during the day to clear your mind

"""
        
        # Work pattern recommendations
        if pattern_score > 15:
            recommendations += """⚖️ WORK-LIFE BALANCE:
• Establish a strict "digital sunset" - no work emails after 7 PM
• Optimize your sleep schedule: aim for 7-8 hours consistently
• Use the Pomodoro Technique: 25 minutes focused work, 5-minute breaks
• Create a dedicated workspace if working from home
• Schedule non-negotiable personal time in your calendar
• Consider delegating tasks that don't require your specific expertise

"""
        
        # General recommendations based on overall score
        if score > 60:
            recommendations += """🚨 IMMEDIATE ACTIONS (High Fatigue):
• Take a mental health day this week if possible
• Speak with your manager about workload distribution
• Consider professional counseling or employee assistance programs
• Postpone non-critical projects by 1-2 weeks
• Implement daily meditation (even 5 minutes helps)

"""
        elif score > 30:
            recommendations += """⚠️ PREVENTIVE MEASURES (Moderate Fatigue):
• Schedule regular "focus blocks" without meetings
• Use the "Two-List Strategy": prioritize your top 5 most important tasks
• Implement "email batching" - check emails only 3 times per day
• Take your full lunch break away from your desk
• Plan weekend activities that energize you

"""
        else:
            recommendations += """✅ MAINTENANCE STRATEGIES (Low Fatigue):
• Continue your current healthy practices
• Monitor your fatigue levels weekly using this tool
• Share your successful strategies with colleagues
• Consider mentoring others who might be struggling with fatigue
• Regularly review and optimize your productivity systems

"""
        
        # Optimal meeting scheduling suggestions
        recommendations += """📅 OPTIMAL MEETING SCHEDULING:

BEST TIMES FOR MEETINGS:
• Tuesday-Thursday: 10:00 AM - 11:30 AM (Peak energy)
• Tuesday-Thursday: 2:00 PM - 3:30 PM (Post-lunch recovery)

AVOID SCHEDULING:
• Monday mornings (transition time)
• Friday afternoons (wind-down period)
• Right after lunch (1:00-2:00 PM)
• Last hour of the workday

MEETING STRUCTURE TIPS:
• Start with agenda and expected outcomes
• Use the "parking lot" method for off-topic discussions
• End 5 minutes early to allow transition time
• Assign clear action items with owners and deadlines

"""
        
        # Personalized break suggestions
        work_hours = self.work_patterns.get('work_hours', 8)
        if work_hours > 8:
            break_frequency = 90  # minutes
        else:
            break_frequency = 120  # minutes
            
        recommendations += f"""☕ BREAK SCHEDULE:
Based on your {work_hours}-hour workday, take a 5-10 minute break every {break_frequency} minutes:

• Micro-breaks: 2-3 minutes every 30 minutes (look away from screen)
• Short breaks: 5-10 minutes every {break_frequency} minutes (walk, stretch)
• Meal breaks: 30-60 minutes (away from workspace)
• Weekly: One full day without work-related activities

EFFECTIVE BREAK ACTIVITIES:
• Deep breathing exercises (4-7-8 technique)
• Light stretching or yoga poses
• Brief walk outside (natural light exposure)
• Hydrate and have a healthy snack
• Quick meditation or mindfulness practice

"""
        
        self.recommendations_text.insert(tk.END, recommendations)
        messagebox.showinfo("Recommendations Generated", "Personalized recommendations have been generated based on your data!")
    
    def export_report(self):
        """Export analysis and recommendations to a file"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"fatigue_report_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("MEETING FATIGUE DETECTOR REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Analysis section
                f.write("ANALYSIS:\n")
                f.write(self.analysis_text.get(1.0, tk.END))
                f.write("\n" + "=" * 50 + "\n\n")
                
                # Recommendations section
                f.write("RECOMMENDATIONS:\n")
                f.write(self.recommendations_text.get(1.0, tk.END))
            
            messagebox.showinfo("Export Successful", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

def main():
    root = tk.Tk()
    app = MeetingFatigueDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main()