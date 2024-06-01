from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from PlagiarismApp.models import (
    Lecturer,
    CustomUser,
    Program,
    Department,
    Course,
    Admin,
    Preferences,
)
from datetime import datetime
from random import randint, choice


lecturer_names = [
    "John Smith",
    "Jane Doe",
    "Michael Johnson",
    "Emily Davis",
    "David Wilson",
    "Olivia Taylor",
    "William Davis",
    "Sophia Brown",
    "Daniel Miller",
    "Mchaga Brown",
]

department_names = [
    "CSE",
    "TE",
    "IST",
    "EEE",
    "CIV",
    "MECH",
    "IND",
    "ARCH",
    "GEO",
    "CHEM",
]

course_names = [
    {
        "name": "Introduction to Computer Science",
        "code": "CS101",
    },
    {
        "name": "Introduction to Computer Networking",
        "code": "CN101",
    },
    {
        "name": "Introduction to Operating Systems",
        "code": "OS101",
    },
    {
        "name": "Introduction to Web Development",
        "code": "WD101",
    },
    {
        "name": "Introduction to Programming Languages",
        "code": "PL101",
    },
    {
        "name": "Introduction to Data Structures",
        "code": "DS101",
    },
    {
        "name": "Introduction to Artificial Intelligence",
        "code": "AI101",
    },
    {
        "name": "Introduction to Database Management Systems",
        "code": "DB101",
    },
    {
        "name": "Introduction to Computer Graphics",
        "code": "CG101",
    },
    {
        "name": "Introduction to Software Engineering",
        "code": "SE101",
    },
    {
        "name": "Introduction to Digital Forensics",
        "code": "DF101",
    },
]

program_names = [
    "Bsc in Computer Science",
    "Bsc in Cyber Security and Digital Forensics Engineering",
    "Bsc in Software Engineering",
    "Bsc in Telecommunication Engineering",
    "Bsc in Health Information System",
    "Bsc in Information System",
    "Bsc in Information Technology",
    "Bsc in Electrical and Electronics Engineering",
    "Bsc in Civil Engineering",
    "Bsc in Mechanical Engineering",
]


year = datetime.now().year


class Command(BaseCommand):
    help = "Populates the database with dummy data"

    def handle(self, *args, **kwargs):

        # Create Doctor instances
        for x in range(10):
            user = CustomUser.objects.create(
                username=f"E/UDOM/{year}/00{x + 1 if x < 9 else 10}",
                email=f"{lecturer_names[x].lower().replace(' ', '.')}@udom.ac.tz",
                password=make_password("lecturer123"),
                first_name=lecturer_names[x].split()[0],
                last_name=lecturer_names[x].split()[1],
                is_staff=True,
                is_active=True,
            )

            Preferences.objects.create(
                user=user,
                theme=choice(["light", "dark"]),
            )

            department = Department.objects.create(name=department_names[x])

            lecturer = Lecturer.objects.create(
                employee_id=user.username, department=department, user=user
            )

            program = Program.objects.create(
                name=program_names[x],
                duration=choice(["1 Year", "2 Years", "3 Years", "4 Years"]),
                department=department,
            )

            course = Course.objects.create(
                name=course_names[x]["name"],
                code=course_names[x]["code"],
                credits=randint(6, 10),
                semester=choice(["I", "II"]),
            )

            course.programs.add(program)
            course.lecturers.add(lecturer)

        CustomUser.objects.create(
            username=f"A/UDOM/{year}/000",
            email="admin@udom.ac.tz",
            password=make_password("admin123"),
            first_name="John",
            last_name="Doe",
            is_active=True,
            is_superuser=True,
        )

        # Create Admin
        Admin.objects.create(
            employee_id=f"A/UDOM/{year}/000",
            user=CustomUser.objects.get(username=f"A/UDOM/{year}/000"),
        )

        # Create Preference
        Preferences.objects.create(
            user=CustomUser.objects.get(username=f"A/UDOM/{year}/000"),
            theme=choice(["light", "dark"]),
            )

        self.stdout.write(self.style.SUCCESS("Database populated successfully"))
