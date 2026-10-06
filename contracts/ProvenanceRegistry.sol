// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ProvenanceRegistry
/// @notice Timestamps research records by their Merkle root on Monad.
///
/// Deliberately the smallest thing that does the job. It has no owner, no admin
/// function, no upgrade path and no way to receive or hold value. There is
/// nothing here to rug, nothing to pause, and nothing whose key could be lost.
/// The entire contract is the two functions below.
///
/// WHAT AN ANCHOR PROVES: that a specific record existed by the block it landed
/// in, and has not changed since. That is a timestamp and a tamper seal.
///
/// WHAT IT DOES NOT PROVE: that the record is correct. A placeholder number,
/// once anchored, is a placeholder number with a block next to it. Permanence
/// is not evidence, and this contract cannot check the science. Callers are
/// expected to refuse synthetic data before it ever reaches here -- see
/// server/chain_anchor.py, which does exactly that.
contract ProvenanceRegistry {
    /// @dev First anchor wins. Re-anchoring the same root is allowed (anyone may
    /// attest to a root) but never overwrites the original block, because the
    /// earliest timestamp is the one that carries the evidentiary weight.
    struct Record {
        address firstAnchoredBy;
        uint64 firstBlock;
        uint64 firstTimestamp;
        uint32 anchorCount;
    }

    mapping(bytes32 => Record) private _records;

    event Anchored(
        address indexed anchoredBy,
        bytes32 indexed root,
        string label,
        uint256 timestamp
    );

    error EmptyRoot();

    /// @notice Anchor a Merkle root, with an optional human-readable label.
    /// @param root  32-byte Merkle root from the caller's content store.
    /// @param label Free text (e.g. a run id). Emitted, never stored, to keep gas flat.
    function anchor(bytes32 root, string calldata label) external {
        if (root == bytes32(0)) revert EmptyRoot();

        Record storage rec = _records[root];
        if (rec.firstBlock == 0) {
            rec.firstAnchoredBy = msg.sender;
            rec.firstBlock = uint64(block.number);
            rec.firstTimestamp = uint64(block.timestamp);
        }
        unchecked {
            rec.anchorCount++;
        }

        emit Anchored(msg.sender, root, label, block.timestamp);
    }

    /// @notice Look up when a root was first anchored.
    /// @return exists  false if this root has never been anchored. A false here
    ///         means "not in this registry", NOT "this record is fraudulent".
    function recordOf(bytes32 root)
        external
        view
        returns (
            bool exists,
            address firstAnchoredBy,
            uint64 firstBlock,
            uint64 firstTimestamp,
            uint32 anchorCount
        )
    {
        Record storage rec = _records[root];
        return (
            rec.firstBlock != 0,
            rec.firstAnchoredBy,
            rec.firstBlock,
            rec.firstTimestamp,
            rec.anchorCount
        );
    }
}
