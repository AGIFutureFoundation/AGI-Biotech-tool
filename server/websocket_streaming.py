"""Real-time WebSocket streaming for VR data updates.

Streams:
- Docking progress (ligand positions, scores)
- Molecular dynamics trajectories
- Analysis results
- Agent state changes
- Conversation updates
"""
import asyncio
import json
import synthetic_provenance as sp
from typing import Dict, Set, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StreamingServer:
    """Manages WebSocket connections and real-time data streaming."""
    
    def __init__(self):
        self.clients: Set[str] = set()
        self.stream_handlers: Dict[str, Callable] = {}
        self.active_streams: Dict[str, Dict] = {}

    async def register_client(self, client_id: str):
        """Register a new client connection."""
        self.clients.add(client_id)
        logger.info(f"Client registered: {client_id} (total: {len(self.clients)})")

    async def unregister_client(self, client_id: str):
        """Unregister client on disconnect."""
        self.clients.discard(client_id)
        logger.info(f"Client unregistered: {client_id}")

    async def broadcast(self, message: Dict, exclude_client: str = None):
        """Broadcast message to all connected clients."""
        for client_id in self.clients:
            if exclude_client and client_id == exclude_client:
                continue
            # In production, use WebSocket send
            logger.debug(f"Send to {client_id}: {message['type']}")

    async def stream_docking_progress(self, campaign_id: str, docking_data: Dict):
        """Stream docking progress in real-time."""
        stream_key = f"docking_{campaign_id}"
        self.active_streams[stream_key] = {
            'type': 'docking',
            'campaign_id': campaign_id,
            'data': docking_data,
            'started_at': datetime.utcnow().isoformat(),
        }
        
        # Simulate streaming updates every 500ms
        for i in range(docking_data.get('total_compounds', 50)):
            update = {
                'type': 'docking_progress',
                'campaign_id': campaign_id,
                'progress': (i + 1) / docking_data.get('total_compounds', 50),
                'current_compound': i + 1,
                'recent_poses': docking_data.get('poses', [])[:3],  # Top 3
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            await self.broadcast(update)
            await asyncio.sleep(0.5)  # Simulate work
        
        del self.active_streams[stream_key]

    async def stream_md_trajectory(self, simulation_id: str, trajectory_frames: list):
        """Stream molecular dynamics trajectory frames."""
        stream_key = f"md_{simulation_id}"
        self.active_streams[stream_key] = {
            'type': 'md',
            'simulation_id': simulation_id,
            'started_at': datetime.utcnow().isoformat(),
        }
        
        for frame_idx, frame in enumerate(trajectory_frames):
            update = {
                'type': 'md_frame',
                'simulation_id': simulation_id,
                'frame_number': frame_idx,
                'total_frames': len(trajectory_frames),
                'progress': (frame_idx + 1) / len(trajectory_frames),
                'ligand_coords': frame.get('ligand_position'),
                'energy': frame.get('energy', 0),
                'temperature': frame.get('temperature', 300),
                'rmsd': frame.get('rmsd', 0),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            await self.broadcast(update)
            await asyncio.sleep(0.1)  # 10 fps for trajectory
        
        del self.active_streams[stream_key]

    async def stream_analysis_results(self, analysis_id: str, results_data: Dict):
        """Stream analysis results as they're computed."""
        stream_key = f"analysis_{analysis_id}"
        self.active_streams[stream_key] = {
            'type': 'analysis',
            'analysis_id': analysis_id,
            'started_at': datetime.utcnow().isoformat(),
        }
        
        # Stream hotspot detection
        if 'hotspots' in results_data:
            for hotspot_idx, hotspot in enumerate(results_data['hotspots']):
                update = {
                    'type': 'hotspot_found',
                    'analysis_id': analysis_id,
                    'hotspot': hotspot,
                    'index': hotspot_idx,
                    'total_hotspots': len(results_data['hotspots']),
                    'timestamp': datetime.utcnow().isoformat(),
                }
                await self.broadcast(update)
                await asyncio.sleep(0.2)
        
        # Stream synthesis predictions
        if 'synthesis_predictions' in results_data:
            for pred_idx, pred in enumerate(results_data['synthesis_predictions']):
                update = {
                    'type': 'sa_score',
                    'analysis_id': analysis_id,
                    'compound': pred['compound_id'],
                    'sa_score': pred['sa_score'],
                    'difficulty': pred['difficulty'],
                    'timestamp': datetime.utcnow().isoformat(),
                }
                await self.broadcast(update)
                await asyncio.sleep(0.1)
        
        del self.active_streams[stream_key]

    async def stream_agent_communication(self, sender: str, receiver: str, message: Dict):
        """Stream agent-to-agent communication."""
        update = {
            'type': 'agent_message',
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }
        await self.broadcast(update)

    def get_active_streams(self) -> Dict:
        """List all active streams."""
        return {
            'count': len(self.active_streams),
            'streams': list(self.active_streams.keys()),
            'clients_connected': len(self.clients),
        }

class VRDataFrame:
    """Structured data frame for VR visualization."""
    
    def __init__(self, frame_type: str):
        self.frame_type = frame_type
        self.timestamp = datetime.utcnow().isoformat()
        self.data = {}

    @staticmethod
    def docking_update(campaign_id: str, compound_id: str, score: float, poses: list) -> 'VRDataFrame':
        """Create docking update frame."""
        frame = VRDataFrame('docking')
        frame.data = {
            'campaign_id': campaign_id,
            'compound_id': compound_id,
            'score': score,
            'poses': poses,
        }
        return frame

    @staticmethod
    def md_frame(simulation_id: str, frame_num: int, ligand_coords: list, energy: float) -> 'VRDataFrame':
        """Create MD trajectory frame."""
        frame = VRDataFrame('md_frame')
        frame.data = {
            'simulation_id': simulation_id,
            'frame_number': frame_num,
            'ligand_coords': ligand_coords,
            'energy': energy,
        }
        return frame

    @staticmethod
    def analysis_update(analysis_id: str, finding_type: str, finding_data: Dict) -> 'VRDataFrame':
        """Create analysis update frame."""
        frame = VRDataFrame('analysis')
        frame.data = {
            'analysis_id': analysis_id,
            'finding_type': finding_type,
            'finding': finding_data,
        }
        return frame

    def to_json(self) -> str:
        """Serialize to JSON for WebSocket transmission.

        sp.dumps keeps the SYNTHETIC marker: a streamed frame carries live
        result values, and json.dumps would write placeholders as plain floats.
        """
        return sp.dumps({
            'frame_type': self.frame_type,
            'timestamp': self.timestamp,
            'data': self.data,
        })
