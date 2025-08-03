#!/bin/bash

# Function 1: Clean temporary and cache files
clean_temp_files() {
    echo "🧹 Cleaning temp and cache files..."
    sudo rm -rf /tmp/*
    rm -rf ~/.cache/*
    sudo rm -rf /var/tmp/*
    echo "✅ Temp files cleaned."
}

# Function 2: List largest files/folders and allow deletion
list_large_files() {
    echo "🔍 Top 20 largest files and folders:"
    sudo du -ah / 2>/dev/null | sort -rh | head -n 20 > /tmp/top_large_files.txt
    cat /tmp/top_large_files.txt

    echo
    read -p "Would you like to delete any non-critical files from the list? (y/n): " del_choice
    if [[ "$del_choice" =~ ^[Yy]$ ]]; then
        echo
        echo "Select the line numbers to delete (e.g. 1 3 5), or press Enter to skip:"
        nl /tmp/top_large_files.txt
        read -a lines

        for i in "${lines[@]}"; do
            file_path=$(sed "${i}q;d" /tmp/top_large_files.txt | awk '{for(i=2;i<=NF;++i) printf $i " "; print ""}')
            echo "Attempting to delete: $file_path"
            sudo rm -ri "$file_path"
        done
    else
        echo "❎ Skipped deletion."
    fi
}

# Function 3: List manually installed packages and allow backup/uninstall/restore
list_extra_manual_packages() {
    echo "📦 Manually installed packages (not from base system):"
    comm -23 <(apt-mark showmanual | sort) <(gzip -cd /var/log/installer/initial-status.gz | awk '/^Package: / { print $2 }' | sort) > /tmp/manual_packages.txt
    cat /tmp/manual_packages.txt

    echo
    read -p "Do you want to uninstall any of these apps with backup? (y/n): " uninstall_choice
    if [[ "$uninstall_choice" =~ ^[Yy]$ ]]; then
        read -p "Enter the package name to uninstall: " app_name

        mkdir -p ~/app_backups/"$app_name"

        echo "📦 Backing up config/data for $app_name..."

        cp -r ~/.config/"$app_name" ~/app_backups/"$app_name"/ 2>/dev/null
        cp -r ~/.local/share/"$app_name" ~/app_backups/"$app_name"/ 2>/dev/null
        sudo cp -r /etc/"$app_name" ~/app_backups/"$app_name"/ 2>/dev/null

        tar -czf ~/app_backups/"$app_name".tar.gz -C ~/app_backups "$app_name"
        rm -rf ~/app_backups/"$app_name"

        echo "✅ Backup saved at: ~/app_backups/${app_name}.tar.gz"

        echo "🗑️ Uninstalling $app_name..."
        sudo apt remove --purge "$app_name" -y
        sudo apt autoremove -y
        echo "✅ $app_name removed."
    fi

    echo
    read -p "Do you want to restore a previously backed-up app? (y/n): " restore_choice
    if [[ "$restore_choice" =~ ^[Yy]$ ]]; then
        read -p "Enter the path to the backup tar.gz file: " backup_file
        read -p "Enter the original app name (for directory restoration): " restore_app

        mkdir -p ~/restore_temp
        tar -xzf "$backup_file" -C ~/restore_temp/

        echo "📁 Restoring data to original locations..."
        cp -r ~/restore_temp/"$restore_app"/.config/"$restore_app" ~/.config/ 2>/dev/null
        cp -r ~/restore_temp/"$restore_app"/.local/share/"$restore_app" ~/.local/share/ 2>/dev/null
        sudo cp -r ~/restore_temp/"$restore_app"/ /etc/ 2>/dev/null

        echo "✅ Restoration completed. You may reinstall '$restore_app' now."
        rm -rf ~/restore_temp
    fi
}

# Function 4: List old Snap revisions
list_old_snaps() {
    echo "📋 Snap packages with old revisions:"
    snap list --all | awk '!/^Name/ {print $1, $2, $3}' | while read name version rev; do
        current=$(snap list "$name" | grep -v "disabled" | awk '{print $3}' | tail -n 1)
        if [[ "$rev" != "$current" ]]; then
            echo "$name $version (revision $rev)"
        fi
    done
}

# Function 5: Remove old Snap revisions
remove_old_snaps() {
    echo "🗑️ Removing old Snap revisions..."
    snap list --all | awk '/disabled/{print $1, $3}' | while read name rev; do
        echo "Removing $name revision $rev..."
        sudo snap remove "$name" --revision="$rev"
    done
    echo "✅ Old revisions removed."
}

# Function 6: Uninstall Snap package
uninstall_snap() {
    echo "📦 Installed Snap packages:"
    snap list
    echo
    read -p "Enter Snap package name to uninstall: " snap_name
    if snap list | grep -q "^$snap_name "; then
        sudo snap remove "$snap_name"
        echo "✅ '$snap_name' removed."
    else
        echo "❌ Snap package '$snap_name' not found."
    fi
}

# Function 7: APT cleanup
apt_cleanup() {
    echo "🧹 Cleaning APT cache and removing unused packages..."
    sudo apt autoremove -y
    sudo apt clean
    echo "✅ APT cleanup done."
}

# Function 8: Optimize Snap storage usage
optimize_snap_storage() {
    echo "📦 Optimizing Snap storage..."

    echo "🔧 Limiting Snap to retain only 1 revision per package..."
    sudo snap set system refresh.retain=1

    echo "🧹 Removing disabled Snap revisions..."
    snap list --all | awk '/disabled/{print $1, $3}' | while read name rev; do
        echo "Removing $name revision $rev..."
        sudo snap remove "$name" --revision="$rev"
    done

    echo "🗑️ Clearing Snap cache..."
    sudo rm -rf /var/cache/snapd
    echo "✅ Snap storage optimized."
}

# Function 9: Clean VS Code extension and app cache (safe login-preserving)
clean_vscode_cache() {
    echo "🧹 Cleaning Visual Studio Code extension cache (safe mode)..."

    CODE_CACHE_DIR="$HOME/.config/Code"

    if [ -d "$CODE_CACHE_DIR" ]; then
        echo "🧼 Removing: Cache/, CachedData/, Service Worker/CacheStorage/"
        rm -rf "$CODE_CACHE_DIR/Cache"
        rm -rf "$CODE_CACHE_DIR/CachedData"
        rm -rf "$CODE_CACHE_DIR/'Service Worker'/CacheStorage"
        echo "✅ VS Code extension cache cleaned safely."
    else
        echo "❌ VS Code config directory not found. Skipping."
    fi
}

# Main Menu
while true; do
    echo
    echo "====== 🛠️ Linux System Cleanup Menu ======"
    echo "1. Clean temp and cache files"
    echo "2. List top 20 largest files/folders (with deletion option)"
    echo "3. List manually installed packages (uninstall with backup/restore)"
    echo "4. List old Snap revisions"
    echo "5. Remove old Snap revisions"
    echo "6. Uninstall a Snap package"
    echo "7. APT autoremove + clean"
    echo "8. Exit"
    echo "9. Optimize Snap storage (remove old versions + shrink size)"
    echo "10. Clean VS Code extension cache (without logout)"
    echo "==========================================="
    read -p "Choose an option [1-10]: " choice

    case $choice in
        1) clean_temp_files ;;
        2) list_large_files ;;
        3) list_extra_manual_packages ;;
        4) list_old_snaps ;;
        5) remove_old_snaps ;;
        6) uninstall_snap ;;
        7) apt_cleanup ;;
        8) echo "👋 Exiting. Stay clean!"; exit 0 ;;
        9) optimize_snap_storage ;;
        10) clean_vscode_cache ;;
        *) echo "❌ Invalid option. Please choose 1-10." ;;
    esac
done
