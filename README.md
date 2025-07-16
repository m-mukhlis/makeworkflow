# Work Item State Tracker

## Background

Our team uses Azure DevOps for project management. We need a service that mirrors work item state changes to support custom reporting and analytics that Azure DevOps doesn't provide out of the box.

## Your Task

We've started building a webhook receiver for Azure DevOps state change events. Your job is to:

1. Complete the webhook endpoint implementation
2. Store state transitions in a way that allows us to:
   - Track the complete history of state changes
   - Calculate time spent in each state
   - Know who moved items and when
3. Handle real-world scenarios appropriately

## Time Limit

⏱️ **You have 1 hour to complete this task.**

## Getting Started

1. Install requirements
   - `pip install -r requirements.txt`
2. Run the fastapi server in development mode
   - `fastapi dev app/main.py`
3. The API docs will be available at http://localhost:8000/docs

## Tests

You can find tests in the `tests/` directory. Run them with:

`python test_solution.py`

## What We're Looking For

- Clean, readable code
- Proper error handling
- Consideration of edge cases
- Clear data modeling decisions

## Important Notes

📁 Explore the repository - there might be useful files beyond just the main code

🤔 Make reasonable assumptions where requirements are unclear

📝 Add brief comments for any significant decisions

⚠️ Real-world webhooks can be messy (missing data, duplicates, out-of-order delivery)


## Deliverables

### When you're done

Commit all your changes and include a brief SOLUTION.md file with:

1. Any assumptions you made
2. Anything you'd do differently with more time
3. Any questions you'd ask in a real scenario

## Questions?

Since this is a time-boxed exercise, make your best judgment on unclear requirements. Document your assumptions rather than getting blocked.
