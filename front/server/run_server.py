#!/usr/bin/env python3
"""
Simple server runner with proper Ctrl+C handling
"""
import sys
import asyncio
from server import FreelainceServer

async def main():
    server = FreelainceServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print('\n🛑 Received Ctrl+C, shutting down...')
        await server.send_shutdown_message()
        print('✅ Server stopped cleanly')
    except Exception as e:
        print(f'💥 Error: {e}')
    finally:
        print('👋 Goodbye!')
        return

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n✅ Forced exit')
    finally:
        sys.exit(0)