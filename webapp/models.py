from django.db import models

# ----------------------------
# Custom User
# ----------------------------
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=[
        ("community", "Community"),
        ("ngo", "NGO"),
        ("authority", "Authority"),
        ("admin", "Admin"),
    ])
    location = models.CharField(max_length=255, null=True, blank=True)
    points = models.IntegerField(default=0)
    badges = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name


# ----------------------------
# User Profile
# ----------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profiles/", null=True, blank=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"{self.user.name}'s Profile"


# ----------------------------
# Report
# ----------------------------
class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    description = models.TextField()
    photo_url = models.CharField(max_length=255)
    geotag_lat = models.FloatField()
    geotag_long = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'report'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-timestamp']


# ----------------------------
# Leaderboard
# ----------------------------
class Leaderboard(models.Model):
    leaderboard_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="leaderboard")
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    class Meta:
        db_table = "leaderboard"

    def __str__(self):
        return f"{self.user.name} - {self.points} pts"

# ----------------------------
# Reward
# ----------------------------
class Reward(models.Model):
    reward_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    points_required = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "rewards"

    def __str__(self):
        return self.title

    # helper to check if a user already claimed it
    def is_claimed_by(self, user):
        return self.claimed_rewards.filter(user=user).exists()


# ----------------------------
# UserReward
# ----------------------------
class UserReward(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_rewards")
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name="claimed_rewards")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_rewards"
        unique_together = ("user", "reward")  # prevent claiming same reward twice

    def __str__(self):
        return f"{self.user.name} claimed {self.reward.title}"
