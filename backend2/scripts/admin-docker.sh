#!/bin/bash
# Admin management script for Docker environment

case $1 in
    "create")
        echo "Creating admin user..."
        docker compose exec api python scripts/admin.py create "$2" "$3" --name "$4"
        ;;
    "reset-password")
        echo "Resetting admin password..."
        docker compose exec api python scripts/admin.py reset-password "$2" "$3"
        ;;
    "list")
        echo "Listing admin users..."
        docker compose exec api python scripts/admin.py list
        ;;
    *)
        echo "Usage: $0 {create|reset-password|list}"
        echo ""
        echo "Examples:"
        echo "  $0 create admin@example.com password123 'Admin Name'"
        echo "  $0 reset-password admin@example.com newpassword123"
        echo "  $0 list"
        exit 1
        ;;
esac
