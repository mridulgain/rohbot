{ pkgs }: {
  deps = [
    pkgs.gdb
    pkgs.mcron
    pkgs.vim
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
}