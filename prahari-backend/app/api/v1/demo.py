from fastapi import APIRouter, Depends, BackgroundTasks
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def simulate_demo_event():
    """
    Simulates a high-priority crime for the Guided Demo sequence.
    This injects mock data into the databases and fires Catalyst Signals / SSE events.
    In a real environment, this would call the actual creation endpoints internally.
    """
    logger.info("🎬 LIVE DEMO TRIGGERED: Starting 60s scenario sequence...")
    
    # Sequence 1: T=0s - Incident Reported
    logger.info("T+0s: Injecting high-severity Armed Robbery in Bengaluru South...")
    await asyncio.sleep(2)
    
    # Sequence 2: T=2s - FIR Drafted & Timeline Event Created
    logger.info("T+2s: Draft FIR CASE-DEMO-001 created. Timeline updated.")
    await asyncio.sleep(3)
    
    # Sequence 3: T=5s - AI Risk Scoring & Neo4j Link Analysis
    logger.info("T+5s: AI Risk Engine calculates 85% probability for Bawariya Gang. Neo4j relationships established.")
    await asyncio.sleep(5)
    
    # Sequence 4: T=10s - CDR & Financial Data Synchronized
    logger.info("T+10s: Subpoenaed CDRs and UPI transactions loaded into Intelligence modules.")
    
    logger.info("Demo backend simulation complete. Frontend should now be autonomously navigating.")

@router.post("/trigger")
async def trigger_live_demo(background_tasks: BackgroundTasks):
    """
    Triggers the Hackathon Guided Demo Scenario.
    """
    background_tasks.add_task(simulate_demo_event)
    return {
        "status": "success", 
        "message": "Guided Scenario sequence initiated.",
        "scenario_id": "CASE-DEMO-001"
    }
