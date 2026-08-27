"""
Contains templates for emails to be sent to CC, SLO, SLC and the club
regarding the achievement's approval and its status to interested parties.
"""

from string import Template

# Email Templates

# email template requesting approval for an achievement to
# CC(Clubs Council) and SLO(Student Life Office) 
# common subject but 3 different bodies

CREATE_ACHIEVEMENT_SUBJECT = Template(
    """
    [Achievements] Approval request for $achievement
    """
)

CREATE_ACHIEVEMENT_BODY = Template(
    """
    $club is requesting you to review and approve their achievement, $achievement.
    
    To view more details and approve or reject the achievement, visit the link below:
    $achievementlink
    
    
    Note: This automated email has been generated from the Clubs Council website. For more details, visit clubs.iiit.ac.in.
    """  # noqa: E501
)

# Email Templates For Clubs

# email template informing the club regarding the status of the achievements
# approval.
# regarding processing, approval and rejection status of the achievement
# if the achievement was deleted by the CC.

APPROVED_ACHIEVEMENT_SUBJECT = Template(
    """
    [Achievements] $achievement_id: Approved $achievement
    """
)

APPROVED_ACHIEVEMENT_BODY_FOR_CLUB = Template(
    """
Dear club,

Your achievement, $achievement, has been approved.

To view more details, visit the link below:
$achievementlink


Note: This automated email has been generated from the Clubs Council website. For more details, visit clubs.iiit.ac.in.
"""  # noqa: E501
)

REJECT_ACHIEVEMENT_SUBJECT = Template(
    """
[Achievements] $achievement_id: $achievement Rejected
"""
)

REJECT_ACHIEVEMENT_BODY_FOR_CLUB = Template(
    """
Dear club,

Your achievement, $achievement, has been rejected by $rejected_by.

To update the achievement details, please visit the following link:
$achievementlink

Best regards,
Clubs Council.


Note: This automated email has been generated from the Clubs Council website. For more details, visit clubs.iiit.ac.in.
"""  # noqa: E501
)
