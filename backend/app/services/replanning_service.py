from backend.app.models.recovery_attempt import RecoveryAttempt


class ReplanningService:

    def get_failed_action_ids(
        self,
        attempts: list[RecoveryAttempt],
    ) -> set[str]:

        return {
            attempt.action_id
            for attempt in attempts
            if attempt.status == "FAILED"
        }

    def filter_failed_actions(
        self,
        action_ids: list[str],
        attempts: list[RecoveryAttempt],
    ) -> list[str]:

        failed_ids = self.get_failed_action_ids(attempts)

        return [
            action_id
            for action_id in action_ids
            if action_id not in failed_ids
        ]

    def next_attempt_number(
        self,
        attempts: list[RecoveryAttempt],
    ) -> int:

        if not attempts:
            return 1

        return max(
            attempt.attempt_number
            for attempt in attempts
        ) + 1