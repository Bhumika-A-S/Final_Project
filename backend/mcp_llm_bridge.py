import requests
import os
import re


class MCPLLMBridge:

    def __init__(self, backend_url: str, auth_token: str = "", openai_api_key: str = None):
        self.backend_url = backend_url
        self.auth_token = auth_token or os.getenv("TIPTRACK_MCP_TOKEN")
        print("MCP TOKEN:", self.auth_token)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.auth_token}"
        }

    def _get(self, endpoint: str):
        url = f"{self.backend_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }

        print("REQUEST URL:", url)
        print("HEADERS:", headers)

        return requests.get(url, headers=headers)

    def _extract_waiter_id(self, question: str):
        """
        Detect waiter ID like W001, W002 from the question.
        """
        match = re.search(r'\bW\d+\b', question.upper())
        if match:
            return match.group(0)

        # default fallback
        return "W001"

    def process_query(self, question: str):

        question_lower = question.lower()
        print("AI QUESTION:", question_lower)

        try:

            # detect waiter id automatically
            waiter_id = self._extract_waiter_id(question)

            # -------------------------
            # BEST WAITER
            # -------------------------
            best_waiter_keywords = [
                "best waiter",
                "top waiter",
                "highest rating",
                "most tips",
                "who earned most",
                "who is best",
                "best performing waiter"
            ]

            if any(word in question_lower for word in best_waiter_keywords):

                r = self._get("/insights/team")

                if r.status_code == 200:
                    data = r.json()
                    leaderboard = data.get("leaderboard", [])

                    if leaderboard:
                        best = leaderboard[0]

                        avg_rating = round(best["avg_rating"], 2)

                        return {
                            "answer": f"The best waiter is {best['name']} with {best['num_tips']} tips and an average rating of {avg_rating}.",
                            "tools_used": [{"tool": "best_waiter"}],
                            "success": True
                        }

            # -------------------------
            # TEAM INSIGHTS
            # -------------------------
            team_keywords = [
                "team",
                "team insights",
                "team performance",
                "overall performance",
                "restaurant performance",
                "staff performance"
            ]

            if any(word in question_lower for word in team_keywords):

                r = self._get("/insights/team")

                if r.status_code == 200:
                    data = r.json()

                    return {
                        "answer": f"The team processed {data['total_orders']} total orders with an overall score of {data['overall_score']}.",
                        "tools_used": [{"tool": "team_insights"}],
                        "success": True
                    }

            # -------------------------
            # TRANSACTIONS
            # -------------------------
            transaction_keywords = [
                "transactions",
                "transaction",
                "recent tips",
                "recent transactions",
                "how many transactions",
                "total transactions"
            ]

            if any(word in question_lower for word in transaction_keywords):

                r = self._get("/transactions")

                if r.status_code == 200:
                    data = r.json()

                    return {
                        "answer": f"There are {len(data)} transactions recorded in the system.",
                        "tools_used": [{"tool": "transactions"}],
                        "success": True
                    }

            # -------------------------
            # WAITER SUMMARY
            # -------------------------
            summary_keywords = [
                "waiter summary",
                "waiter performance",
                "waiter tips",
                "tips of waiter",
                "how many tips",
                "summary",
                "tip summary",
                "performance"
            ]

            if any(word in question_lower for word in summary_keywords):

                r = self._get(f"/waiters/{waiter_id}/summary")

                if r.status_code == 200:
                    data = r.json()

                    avg_rating = round(data["avg_rating"], 2)

                    return {
                        "answer": f"Waiter {data['waiter_id']} has received {data['total_tips']} in tips from {data['num_tips']} customers with an average rating of {avg_rating}.",
                        "tools_used": [{"tool": "get_waiter_summary"}],
                        "success": True
                    }

            return {
                "answer": "I couldn't find data for that question.",
                "tools_used": [],
                "success": False
            }

        except Exception as e:

            return {
                "answer": str(e),
                "tools_used": [],
                "success": False
            }