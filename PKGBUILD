# Maintainer: DomiLuebben <https://github.com/DomiLuebben>
# Hinweis: Dies ist ein inoffizieller 1:1 Nachbau für Linux.
# Sämtliche Urheberrechte an den Assets liegen bei der Ravensburger Verlag GmbH.
pkgname=tiptoi-manager
pkgver=5.0.2
pkgrel=1
pkgdesc="Nativer tiptoi® Manager für Linux (1:1 Nachbau, alle Assets © Ravensburger Verlag GmbH)"
arch=('any')
url="https://github.com/DomiLuebben/tiptoi-manager-linux"
license=('custom:proprietary')
depends=('python' 'python-pyqt6' 'python-requests' 'udisks2')

package() {
    # Directory where PKGBUILD is located
    local src_root="$startdir"
    local destdir="$pkgdir/usr/lib/tiptoi-manager"
    
    install -dm755 "$destdir"
    cp -r "$src_root/main.py" "$src_root/LocalizationFile.txt" "$src_root/assets" "$src_root/src" "$destdir/"
    
    # Clean any compiled cache files from installation
    find "$destdir" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$destdir" -name "*.pyc" -delete 2>/dev/null || true
    
    # Install launcher script
    install -dm755 "$pkgdir/usr/bin"
    cat << 'EOF' > "$pkgdir/usr/bin/tiptoi-manager"
#!/bin/sh
exec python3 /usr/lib/tiptoi-manager/main.py "$@"
EOF
    chmod 755 "$pkgdir/usr/bin/tiptoi-manager"
    
    # Install desktop entry
    install -Dm644 "$src_root/tiptoi-manager.desktop" "$pkgdir/usr/share/applications/tiptoi-manager.desktop"
    
    # Install desktop icon
    install -Dm644 "$src_root/assets/app_icon.png" "$pkgdir/usr/share/icons/hicolor/256x256/apps/tiptoi-manager.png"
}
